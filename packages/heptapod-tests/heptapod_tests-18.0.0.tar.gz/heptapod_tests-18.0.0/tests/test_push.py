import json
import pytest
import re

from heptapod_tests.access_levels import ProjectAccess
from heptapod_tests.hg import (
    LocalRepo,
)
from heptapod_tests.merge_request import MergeRequest
from heptapod_tests.project import (
    extract_gitlab_branch_titles,
)
from heptapod_tests.reverse_calls import HttpListener
from heptapod_tests.runner import job_variables
from heptapod_tests.selenium import (
    assert_webdriver_not_error,
    raw_page_content,
)

from . import needs
from . import suitable


parametrize = pytest.mark.parametrize


def prepare_simple_repo(proj, repo_path):
    repo = LocalRepo.init(repo_path, default_url=proj.owner_basic_auth_url)

    repo_path.join('foo').write('foo0')
    repo.hg('commit', '-Am', "Commit 0")
    repo.hg('phase', '-p', ".")
    repo.hg('topic', 'zetop')

    repo_path.join('foo').write('foo1')
    repo.hg('commit', '-Am', "Commit 1")
    repo.hg('push')
    return repo


@suitable.prod_server
def test_push_basic(test_project, tmpdir):
    """
    Push two changesets, one being a draft, confirm their arrival and phases

    Often used as a smoke test.
    """
    prepare_simple_repo(test_project, tmpdir.join('repo1'))
    # let's control what GitLab really sees
    assert test_project.api_branch_titles() == {
        'branch/default': 'Commit 0',
        'topic/default/zetop': 'Commit 1',
    }
    url = test_project.owner_basic_auth_url

    clone = LocalRepo.clone(url, tmpdir.join('repo2'))
    Extract, extracts = clone.changeset_extracts(('desc', 'phase', 'topic'))
    assert extracts == (
        Extract(desc='Commit 1', phase='draft', topic='zetop'),
        Extract(desc='Commit 0', phase='public', topic=''),
    )


def test_push_webdriver(test_project, tmpdir):
    """
    follow-up on push_basic. Not meaningful if the latter fails
    """
    repo = prepare_simple_repo(test_project, tmpdir.join('repo1'))
    url = test_project.owner_basic_auth_url

    clone = LocalRepo.clone(url, tmpdir.join('repo2'))

    repo.path.join('foo').write('foo2')
    repo.hg('commit', '-Am', "Commit 2")
    repo.hg('push', url)

    clone.hg('pull', url)
    Extract, extracts = clone.changeset_extracts(('desc', 'phase', 'topic'))
    assert extracts == (
        Extract(desc='Commit 2', phase='draft', topic='zetop'),
        Extract(desc='Commit 1', phase='draft', topic='zetop'),
        Extract(desc='Commit 0', phase='public', topic=''),
    )

    # now GitLab side:

    branches = test_project.api_branches()

    assert extract_gitlab_branch_titles(branches) == {
        'branch/default': 'Commit 0',
        'topic/default/zetop': 'Commit 2',
    }

    webdriver = test_project.owner_webdriver

    webdriver.get(test_project.url)
    assert_webdriver_not_error(webdriver)

    # repository drop-down menu
    menu = {i.lower() for i in test_project.webdriver_repo_new_content_menu()}
    assert 'new branch' not in menu
    assert 'new tag' not in menu

    commit0_id = branches['branch/default']['commit']['id']
    webdriver.get(test_project.commit_page_url(commit0_id))
    assert_webdriver_not_error(webdriver)

    assert 'Commit 0' in webdriver.title
    if test_project.hg_native:
        assert repo.short_node('0') in webdriver.title

    # Commit 0 seems to be problematic also for legacy hg-git based
    # projects (probably because of id to reference null commit)
    commit2_page_url = test_project.commit_page_url(
        branches['topic/default/zetop']['commit']['id'])
    check_commit2_plain_diff(webdriver, commit2_page_url)
    check_commit2_email_patch(webdriver, commit2_page_url,
                              style='hg' if test_project.hg_native else 'git')
    # navigation through a commit can lead to a raw blob download URL
    # that uses its SHA directly
    for rev in ('branch/default', commit0_id):
        assert test_project.webdriver_get_raw_blob('foo', rev) == 'foo0'


def check_commit2_plain_diff(webdriver, commit_page_url):
    """Assertions on Plain Diff page for Commit 2 of test_push_webdriver().

    The primary purpose is to be sure it reached the correct
    (H)Gitaly backend.

    More detailed assertions than the bare minimum are not necessary, as they
    are redundant with internal testing of HGitaly where comprehensive
    comparison tests with Gitaly are provided. They provide another
    perspective, though, which have to be balanced with the effort to write
    and maintain them.
    """
    webdriver.get(commit_page_url + '.diff')
    # there are non-significative trailing whitespace differences
    # between Git and Mercurial, whence the use of `splitlines()`.
    result_lines = raw_page_content(webdriver).splitlines()
    assert result_lines[0] == 'diff --git a/foo b/foo'
    assert result_lines[2:4] == ['--- a/foo',
                                 '+++ b/foo',
                                 ]
    # Git does not display column line numbers in this case
    assert re.match(r'@@ -1(,1)? \+1(,1)? @@', result_lines[4]) is not None
    assert result_lines[5:] == ['-foo1',
                                '\\ No newline at end of file',
                                '+foo2',
                                '\\ No newline at end of file'
                                ]


def check_commit2_email_patch(webdriver, commit_page_url, style):
    """Assertions on Email Patch page for Commit 2 of test_push_webdriver().
    """
    webdriver.get(commit_page_url + '.patch')
    result_lines = raw_page_content(webdriver).splitlines()
    if style == 'hg':
        # not yet an actual email patch, enough to prove content was
        # generated by GetRawPatch before hgitaly#88 is done
        assert '# HG changeset patch' in result_lines
        return

    # Git-based case, for reference and to inspire future assertions
    # in the native Mercurial case once hgitaly#88 is done.
    email_headers = result_lines[:5]

    assert 'Subject: [PATCH] Commit 2' in email_headers

    # change summary
    assert result_lines[6:8] == [
        ' foo | 2 +-',
        ' 1 file changed, 1 insertion(+), 1 deletion(-)',
    ]

    # enough to prove we also have actual diff content
    assert 'diff --git a/foo b/foo' in result_lines[8:]


@needs.reverse_call
def test_web_hook(tmpdir, test_project):
    """Setup a webhook, listen to it, push and record the resulting POST
    """
    listener = HttpListener(test_project.heptapod)
    repo_path = tmpdir.join('repo1')
    url = test_project.owner_basic_auth_url
    test_project.api_post(
        subpath='hooks',
        data=dict(
            id=test_project.id,
            url=listener.url(test_project.heptapod),
            push_events=True,
            enable_ssl_verification=False,
        )
    )

    repo = LocalRepo.init(repo_path)
    repo_path.join('foo').write('foo0')
    repo.hg('commit', '-Am', "Commit 0")
    repo.hg('push', '--publish', url)

    timeout = 30
    exit_code = listener.join(timeout)
    assert exit_code is not None, "No request received in %d seconds" % timeout

    posted = listener.queue.get()
    environ = posted['environ']

    # stuff that we want to be altered about if it changes
    assert environ['CONTENT_TYPE'] == 'application/json'
    assert environ['HTTP_X_GITLAB_EVENT'] == 'Push Hook'

    hook_data = json.loads(posted['body'])
    assert hook_data['ref'] == 'refs/heads/branch/default'
    hgsha = repo.node('.')

    commits = hook_data.get('commits')
    assert commits is not None
    assert len(commits) == 1
    commit = commits[0]
    assert commit['message'].strip() == "Commit 0"
    assert hook_data['checkout_hgsha'] == hgsha
    assert hook_data['hg_before'] == '0' * 40
    assert hook_data['hg_after'] == hgsha
    assert commit['hgid'] == hgsha


@needs.fs_access
@parametrize('push_proto', ['ssh', 'http'])
def test_push_hook_env(test_project, tmpdir, push_proto):
    repo_path = tmpdir.join('repo1')
    repo = LocalRepo.init(repo_path)
    repo_path.join('foo').write('foo0')
    repo.hg('commit', '-Am', "Commit 0")

    test_project.extend_hgrc(
        "[hooks]",
        "pretxnchangegroup.heptapod_env=python:"
        "heptapod.hooks.dev_util.print_heptapod_env")

    if push_proto == 'http':
        out = repo.hg('push', test_project.owner_basic_auth_url)
    elif push_proto == 'ssh':
        out = repo.hg('push', '--ssh', *test_project.owner_ssh_params)

    user = test_project.owner_user
    user_info = user.api_get_info()

    for env_var in [('HEPTAPOD_PROJECT_ID', str(test_project.id)),
                    ('HEPTAPOD_PROJECT_NAMESPACE_FULL_PATH', user.name),
                    ('HEPTAPOD_PROJECT_PATH', test_project.name),
                    ('HEPTAPOD_REPOSITORY_USAGE', 'project'),
                    ('HEPTAPOD_USERINFO_EMAIL', user_info['email']),
                    ('HEPTAPOD_USERINFO_ID', str(user.id)),
                    ('HEPTAPOD_USERINFO_NAME', user_info['name']),
                    ('HEPTAPOD_USERINFO_USERNAME', user.name),
                    ]:
        assert repr(env_var) in out


@parametrize('allowed_to_push', ('publisher-allowed', 'maintainer-allowed'))
def test_protected_branch_refusal(test_project, tmpdir, allowed_to_push):
    """Refusals due to branch protection are explained to the end user."""

    repo_path = tmpdir.join('repo1')
    url = test_project.owner_basic_auth_url

    repo = LocalRepo.init(repo_path)
    # let's have two branches
    repo_path.join('foo').write('foo0')
    repo.hg('commit', '-Am', "Commit 0")
    repo_path.join('foo').write('foo1')
    repo.hg('commit', '-Am', "Commit 1")
    repo.hg('push', url)  # make sure 'default' is the GitLab default branch
    repo.hg('up', '0')
    repo.hg('branch', 'a_branch')
    repo_path.join('foo').write('in branch')
    repo.hg('commit', '-Am', "Commit in branch")
    repo.hg('phase', '-pr', "default+a_branch")
    print(repo.graphlog())
    repo.hg('push', '--new-branch', url)

    # now let's protect the branch
    if allowed_to_push == 'publisher-allowed':
        allowed_level = ProjectAccess.HG_PUBLISHER
        not_allowed_level = ProjectAccess.DEVELOPER
    elif allowed_to_push == 'maintainer-allowed':
        allowed_level = ProjectAccess.MAINTAINER
        not_allowed_level = ProjectAccess.HG_PUBLISHER
    resp = test_project.api_post(
        subpath='protected_branches',
        data=dict(name='branch/a_branch',
                  push_access_level=allowed_level.value,
                  ))
    assert resp.status_code in (200, 201, 202)

    test_project.grant_member_access(user_name='test_basic',
                                     level=not_allowed_level)
    basic_user_url = test_project.basic_auth_url(user_name='test_basic')
    basic_user_ssh_params = test_project.ssh_params('test_basic')

    repo_path.join('foo').write('still in branch')
    repo.hg('commit', '-m', 'New commit that developer cannot push')
    non_closing_sha = repo.node('.')

    repo.assert_hg_failure(
        'push', '--ssh', *basic_user_ssh_params,
        error_message_expectations=re.compile("push.*protected branches"))
    repo.assert_hg_failure(
        'push', basic_user_url,
        error_message_expectations=re.compile("push.*protected branches"))

    # it is also forbidden to remove protected branches
    repo.hg('commit', '--close-branch', '-m', "closing")
    repo.assert_hg_failure(
        'push', basic_user_url,
        error_message_expectations="delete protected branches")

    # the failed pushes had indeed no effect on the hg repo
    clone = LocalRepo.clone(url, tmpdir.join('repo2'))

    Extract, extracts = clone.changeset_extracts(('desc', 'branch'),
                                                 revs='a_branch')

    assert extracts == (
        Extract(desc='Commit in branch', branch='a_branch'),
    )

    test_project.grant_member_access(user_name='test_basic',
                                     level=allowed_level)
    repo.hg('push', '-r', non_closing_sha, basic_user_url)
    clone.hg('pull')

    Extract, extracts = clone.changeset_extracts(('desc', 'branch'),
                                                 revs='a_branch')
    assert extracts == (
        Extract(desc='New commit that developer cannot push',
                branch='a_branch'),
    )


def test_protected_branch_ultimate(test_project, tmpdir):
    """Mode in which even maintainers can't push.

    TODO make part of parametrization of test_protected_branch_refusal
    """

    repo_path = tmpdir.join('repo1')
    url = test_project.owner_basic_auth_url

    repo = LocalRepo.init(repo_path)
    # let's have two branches
    repo_path.join('foo').write('foo0')
    repo.hg('commit', '-Am', "Commit 0")
    repo_path.join('foo').write('foo1')
    repo.hg('commit', '-Am', "Commit 1")
    repo.hg('push', url)  # make sure 'default' is the GitLab default branch
    repo.hg('up', '0')
    repo.hg('branch', 'a_branch')
    repo_path.join('foo').write('in branch')
    repo.hg('commit', '-Am', "Commit in branch")
    repo.hg('phase', '-pr', "default+a_branch")
    print(repo.graphlog())
    repo.hg('push', '--new-branch', url)

    resp = test_project.api_post(subpath='protected_branches',
                                 data=dict(name='branch/a_branch',
                                           push_access_level=0))
    assert resp.status_code in (200, 201, 202)

    repo_path.join('foo').write('still in branch')
    repo.hg('commit', '-m', 'New commit that even Owner cannot push')

    ssh_params = test_project.owner_ssh_params
    repo.assert_hg_failure(
        'push', '--ssh', *ssh_params,
        error_message_expectations=re.compile("push.*protected branches"))
    repo.assert_hg_failure(
        'push', url,
        error_message_expectations=re.compile("push.*protected branches"))

    # regular owner is also instance-wide administrator, and should
    # arguably still be allowed to remove the branch, let's make a Maintainer
    test_project.grant_member_access(user_name='test_basic',
                                     level=ProjectAccess.MAINTAINER)
    maintainer_url = test_project.basic_auth_url(user_name='test_basic')

    repo.hg('commit', '--close-branch', '-m', "closing")
    repo.assert_hg_failure(
        'push', maintainer_url,
        error_message_expectations="delete protected branches")

    # the failed pushes had indeed no effect on the hg repo
    clone = LocalRepo.clone(url, tmpdir.join('repo2'))
    Extract, extracts = clone.changeset_extracts(('desc', 'branch'))
    assert extracts == (
        Extract(desc='Commit in branch', branch='a_branch'),
        Extract(desc='Commit 1', branch='default'),
        Extract(desc='Commit 0', branch='default'),
    )

    # far from being completely blocked the newly appointed Maintainer
    # can still accept MRs

    repo.hg('topic', '-r', '.~1', 'zetop')
    repo.hg('push', '-r', 'zetop', maintainer_url)
    mr = MergeRequest.api_create(test_project,
                                 source_branch='topic/a_branch/zetop',
                                 target_branch='branch/a_branch')

    mr.wait_assert(lambda info: info.get('merge_status') == 'can_be_merged',
                   msg="Mergeability wrong or still unknown")
    mr.api_accept(user=test_project.heptapod.get_user('test_basic'))

    clone.hg('pull')
    Extract, extracts = clone.changeset_extracts(('desc', 'branch', 'phase'),
                                                 collection=set)
    assert extracts == {
        Extract(desc='New commit that even Owner cannot push',
                branch='a_branch',
                phase='public'),
        Extract(desc='Commit in branch', branch='a_branch', phase='public'),
        Extract(desc='Commit 1', branch='default', phase='public'),
        Extract(desc='Commit 0', branch='default', phase='public'),
    }


def test_push_tags_branch_heads(test_project, tmpdir):
    repo_path = tmpdir.join('repo1')

    # Minimal repo with two branches and one root
    repo = LocalRepo.init(repo_path,
                          default_url=test_project.owner_basic_auth_url)
    repo_path.join('foo').write('foo0')
    repo.hg('commit', '-Am', "Commit 0")
    repo_path.join('foo').write('foo1')
    repo.hg('commit', '-Am', "Commit 1")
    repo.hg('push')
    repo.hg('up', '0')
    repo.hg('branch', 'other')
    repo_path.join('foo').write("other")
    repo.hg('commit', '-m', "Commit 2")
    # to reproduce heptapod#96, we need the tag commit not to
    # be the head of the 'other' branch
    repo.hg('up', '1')
    repo.hg('tag', 'other-1.0', '-r', '2')
    print(repo.graphlog())
    repo.hg('push', '--new-branch')

    branches = test_project.api_branches()
    assert set(branches) == {'branch/default', 'branch/other'}
    assert branches['branch/other']['commit']['title'] == 'Commit 2'

    tags = test_project.api_tags()
    assert set(tags) == {'other-1.0'}
    assert tags['other-1.0']['commit']['title'] == "Commit 2"


def test_tag_edit_remove(test_project, tmpdir):
    repo_path = tmpdir.join('repo')
    repo = LocalRepo.init(repo_path,
                          default_url=test_project.owner_basic_auth_url)

    repo_path.join('foo').write('foo0')
    repo.hg('commit', '-Am', "Commit 0")
    repo.hg('tag', 'v1')
    repo.hg('push')
    assert list(test_project.api_tags()) == ['v1']

    repo_path.join('foo').write('foo1')
    repo.hg('commit', '-m', "Commit 1")
    repo.hg('tag', '--force', 'v1')
    repo.hg('push')
    tags = test_project.api_tags()
    assert list(tags) == ['v1']
    assert tags['v1']['commit']['title'] == 'Commit 1'

    repo.hg('tag', '--remove', 'v1')
    repo.hg('push')
    assert not test_project.api_tags()


@suitable.prod_server
def test_push_tag_ci_job(test_project_with_runner, tmpdir):
    proj, runner = test_project_with_runner
    repo_path = tmpdir.join('repo1')

    repo = LocalRepo.init(repo_path, default_url=proj.owner_basic_auth_url)
    repo.init_gitlab_ci()
    repo.hg('tag', '1.0')
    repo.hg('push')
    jobs = runner.wait_assert_jobs(2)

    tag_jobs = [j for j in jobs if j['git_info']['ref_type'] == 'tag']
    assert len(tag_jobs) == 1
    job_vars = job_variables(tag_jobs[0])
    assert job_vars['CI_COMMIT_TAG'] == '1.0'


def test_internal_force_push_default_branch(test_project, tmpdir):
    """
    Although protected, but still accept internal Git force-pushes.
    See heptapod#129
    """
    repo_path = tmpdir.join('repo1')
    url = test_project.owner_basic_auth_url

    # internal force pushes occur upon amending of drafts without topics.
    test_project.api_hgrc_set(inherit=True, auto_publish='nothing')
    repo = LocalRepo.init(repo_path)
    in_repo = repo_path.join('foo')
    in_repo.write('foo0')
    repo.hg('commit', '-Am', "Commit 0")
    repo.hg('phase', '-p', ".")
    in_repo.write('foo1')
    repo.hg('commit', '-Am', "Commit 1")
    repo.hg('push', url)

    assert test_project.api_default_branch() == 'branch/default'
    assert test_project.api_branch_titles() == {'branch/default': 'Commit 1'}

    in_repo.write('amended')
    repo.hg('amend', '-m', "Amended")
    repo.hg('push', url)

    test_project.wait_assert_api_branch_titles({'branch/default': 'Amended'})

    clone = LocalRepo.clone(url, tmpdir.join('repo2'))
    log = clone.hg('log', '-T', '{desc}:{phase}\n')
    assert log.splitlines() == ['Amended:draft', 'Commit 0:public']


def test_auto_publish_abort(test_project, tmpdir):
    """Using `experimental.auto-publish=abort` on the client-side."""
    proj = test_project
    repo_path = tmpdir / 'repo'
    repo = LocalRepo.init(repo_path, default_url=proj.owner_basic_auth_url)

    file_path = repo_path / 'foo'
    file_path.write('foo0')
    repo.hg('commit', '-Am', "Commit 0")
    repo.hg('phase', '-p', ".")
    repo.hg('push')

    file_path.write('foo1')
    repo.hg('commit', '-Am', "Commit 1")

    def assert_phase(rev, phase):
        assert repo.hg('log', '-r', rev, '-T', '{phase}').strip() == phase

    assert_phase('.', 'draft')
    # using auto-publish=abort refuses the push of a draft changeset with
    # no topic because that's an automatic publication
    push_cmd = ['--config', 'experimental.auto-publish=abort',
                'push', '-r', '.']
    repo.assert_hg_failure(*push_cmd)
    assert_phase('.', 'draft')

    # yet explicit push --publish works
    push_cmd.append('--publish')
    repo.hg(*push_cmd)
    assert_phase('.', 'public')


def test_push_subrepos(test_project, tmpdir):
    """
    The server just ignores subrepos in ordinary pushes.
    """
    repo_path = tmpdir.join('repo1')
    other_path = tmpdir.join('repo2')
    nested_path = repo_path.join('nested')
    url = test_project.owner_basic_auth_url

    repo = LocalRepo.init(repo_path)
    other = LocalRepo.init(other_path)
    nested = LocalRepo.init(nested_path)
    repo_path.join('foo').write('foo0')
    repo.hg('commit', '-Am', "Commit 0")
    repo.hg('phase', '-p', ".")

    nested_path.join('bar').write('nestedbar')
    nested.hg('commit', '-Am', "Nested Bar 0")
    nested_sha = nested.hg('log', '-T', '{node}', '-r', '.')
    repo_path.join('.hgsub').write("nested = file://%s\n" % other_path)
    repo.hg('add', '-S')
    repo.hg('commit', '-Am', "Subrepos config")

    # subrepositories system did its job
    substate = repo_path.join('.hgsubstate')
    assert substate.exists()
    assert substate.read().split() == [nested_sha, 'nested']
    repo.hg('push', url)

    # no problem with subsequent pushes
    repo_path.join('foo').write('foo1')
    repo.hg('commit', '-Am', "Commit 1")
    repo.hg('push', url)

    # let's control what GitLab really sees
    assert test_project.api_branch_titles() == {
        'branch/default': 'Commit 1',
    }

    # the subrepo also got pushed successfully
    assert other.hg('log', '-T', '{node}') == nested_sha
