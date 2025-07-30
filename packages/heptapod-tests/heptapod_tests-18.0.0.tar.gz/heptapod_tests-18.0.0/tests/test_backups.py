import os
import pytest
import time

from heptapod_tests.namespace import Group
from heptapod_tests.git import LocalRepo as GitRepo
from heptapod_tests.hg import LocalRepo
from heptapod_tests.merge_request import MergeRequest
from heptapod_tests.project import (
    Project,
    extract_gitlab_branch_titles,
)
from heptapod_tests.utils import (
    unique_name,
)
from heptapod_tests.wait import wait_assert

from . import needs


parametrize = pytest.mark.parametrize


@needs.services
def test_project_restore(project_breaks_concurrent, tmpdir):
    test_project = project_breaks_concurrent

    repo_path = tmpdir.join('repo1')
    url = test_project.owner_basic_auth_url

    repo = LocalRepo.init(repo_path)
    repo_path.join('foo').write('foo0')
    repo.hg('commit', '-Am', "Commit 0")
    repo.hg('phase', '-p', ".")
    repo.hg('topic', 'zetop')
    gl_topic = 'topic/default/zetop'

    repo_path.join('foo').write('foo1')
    repo.hg('commit', '-Am', "Commit 1")
    repo.hg('push', url)

    # heptapod#526: obsoleting Commit 1, keeping note of its SHAs first
    obsolete_hg_sha = repo.node('.')
    gl_branches = test_project.api_branches()
    obsolete_gl_sha = gl_branches[gl_topic]['commit']['id']

    # In hg_git case, we must force GitLab to keep the Git commit around
    # Even with native repositories, given that we are now using gitaly-backup
    # unconditionally, only ancestors of known GitLab refs are considered
    # (see heptapod#679)
    MergeRequest.api_create(test_project, gl_topic)

    repo_path.join('foo').write('foo one')
    repo.hg('amend')
    repo.hg('push', url)

    # To test backup of specific config works
    assert test_project.api_hgrc_set(
        inherit=True, auto_publish='nothing').status_code == 204

    # Create a wiki
    wiki_info = test_project.api_wiki_page_create(
        title="Home", content="# Sweet home")
    assert wiki_info['title'] == "Home"

    heptapod = test_project.heptapod
    heptapod.backup_create()

    # make sure we won't confuse a no-op with a success
    test_project.api_destroy()

    with heptapod.backup_restore():
        # let's control what GitLab really sees
        branches = test_project.api_branches()

        assert extract_gitlab_branch_titles(branches) == {
            'branch/default': 'Commit 0',
            'topic/default/zetop': 'Commit 1',
        }

        webdriver = test_project.owner_webdriver
        webdriver.get(test_project.commit_page_url(
            branches['branch/default']['commit']['id']))

        # we don't have a reliable way to detect an error
        # the title would be just 500 in production and the error class name in
        # development mode.
        assert "Error" not in webdriver.title
        assert "(500)" not in webdriver.title

        assert 'Commit 0' in webdriver.title
        if heptapod.hg_native:
            assert repo.short_node('0') in webdriver.title

        # Now what a Mercurial client sees
        clone = LocalRepo.clone(url, tmpdir.join('repo2'))
        log = clone.hg('log', '-T', '{desc}:{phase}:{topic}\n')
        assert log.splitlines() == ['Commit 1:draft:zetop', 'Commit 0:public:']

        # and for the wiki
        wiki_clone_path = tmpdir.join('wiki')
        LocalRepo.clone(test_project.hg_wiki_url(), wiki_clone_path)
        assert wiki_clone_path.join('Home.md').read() == '# Sweet home'

    # Checking that configuration has been backuped
    repo.hg('up', 'default')
    repo_path.join('foo').write('foo2')
    repo.hg('commit', '-Am', "Commit 2")
    expected_phases = ['Commit 2:draft:', 'Commit 1:draft:zetop',
                       'Commit 0:public:']
    assert repo.hg('log', '-T', '{desc}:{phase}:{topic}\n'
                   ).splitlines() == expected_phases

    repo.hg('push', url)
    clone.hg('pull')
    assert clone.hg('log', '-T', '{desc}:{phase}:{topic}\n'
                    ).splitlines() == expected_phases

    # heptapod#526: obsolete changeset is still present server-side
    obs_commit = test_project.api_get_commit_metadata(obsolete_gl_sha)
    assert obs_commit['hg_id'] == obsolete_hg_sha


@needs.services
@needs.hg_native
@needs.fs_access
def test_project_restore_aux_git_repo(project_breaks_concurrent,
                                      tmpdir):
    """Special case of native Mercurial with an aux Git repo for mirroring."""
    test_project = project_breaks_concurrent
    heptapod = test_project.heptapod

    test_project.hg_git_repo_expected = True

    repo_path = tmpdir.join('repo1')
    url = test_project.owner_basic_auth_url

    repo = LocalRepo.init(repo_path)
    repo_path.join('foo').write('foo0')
    repo.hg('commit', '-Am', "Commit 0")
    repo.hg('phase', '-p', ".")
    repo.hg('push', url)

    git_repo = GitRepo(test_project.fs_path_git)
    expected_branches = {
        'branch/default': 'Commit 0',
    }
    # we need a mirror attempt to fill in the Git repo
    # using an URL that should actually work to avoid various cases of
    # not even starting the mirroring
    tgt_name = 'target_%s' % str(time.time()).replace('.', '_')
    owner = test_project.owner
    with Project.api_create(heptapod, owner, tgt_name,
                            vcs_type='git') as git_tgt:
        mirror = test_project.api_create_mirror(
            url=git_tgt.owner_basic_auth_url,
            enabled=True,
            hg_mirror_type=None,
        )
        mirror.api_trigger()
        wait_assert(lambda: os.path.exists(git_repo.path),
                    lambda info: info)
        wait_assert(lambda: git_repo.branch_titles(),
                    lambda info: info == expected_branches)

    heptapod.backup_create()

    # make sure we won't confuse a no-op with a success
    test_project.api_destroy()

    with heptapod.backup_restore():
        # just making sure the backup/restore generally worked before
        # specific assertions for this test
        assert test_project.api_branch_titles() == expected_branches

    # restoration really worked for the aux Git repo
    # (new instance for when it will become useful)
    git_repo = GitRepo(test_project.fs_path_git)
    assert git_repo.branch_titles() == expected_branches


@needs.services
def test_group_restore(heptapod, breaks_concurrent, tmpdir):
    group = None
    try:
        group_name = unique_name('test_group')
        group = Group.api_create(heptapod, group_name,
                                 user_name='test_basic')
        assert group.path == group_name
        assert group.full_path == group_name
        found = Group.api_search(heptapod, group_name, owner_name='test_basic')
        assert found == group
        project = Project.api_create(heptapod,
                                     project_name='test_proj',
                                     user_name='test_basic',
                                     group=group)
        assert project.api_get_field('path_with_namespace') == '/'.join(
            (group.full_path, 'test_proj'))

        group.put_hgrc(("[experimental]\n",
                        "groupconf=test\n"))
        assert project.hg_config('experimental')['groupconf'] == 'test'

        # empty repo is a special case, let's avoid it
        repo_path = tmpdir.join('repo1')
        url = project.owner_basic_auth_url
        repo = LocalRepo.init(repo_path)
        repo_path.join('foo').write('foo0')
        repo.hg('commit', '-Am', "Commit 0")
        repo.hg('phase', '-p', ".")
        repo.hg('push', url)

        heptapod.backup_create()

        # make sure we won't confuse a no-op with a success
        group.api_delete()

        with heptapod.backup_restore():
            assert project.hg_config('experimental')['groupconf'] == 'test'

    finally:
        if group is not None:
            group.api_delete()
