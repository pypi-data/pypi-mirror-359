from io import BytesIO
import json
import pytest

from heptapod_tests.access_levels import ProjectAccess
from heptapod_tests.content import (
    prepare_import_source_git,
    prepare_import_source_hg,
)
from heptapod_tests.git import LocalRepo as GitRepo
from heptapod_tests.hg import LocalRepo as HgRepo
from heptapod_tests.merge_request import MergeRequest
from heptapod_tests.project import Project
from heptapod_tests.selenium import (
    assert_webdriver_not_error
)
from heptapod_tests.utils import unique_name

from . import (
    suitable,
)
parametrize = pytest.mark.parametrize


@suitable.prod_server
def test_basic(git_project, tmpdir):
    proj = git_project
    repo_path = tmpdir.join('repo')

    # Empty page (instructions)

    webdriver = git_project.owner_webdriver
    webdriver.get(git_project.url)
    assert "git clone" in webdriver.page_source

    # SSH operations

    ssh_cmd, ssh_url = proj.owner_ssh_params

    repo = GitRepo.init(repo_path, default_url=ssh_url)
    repo_path.join('foo').write("Hey this is in Git!\n")
    repo.git('add', 'foo')
    repo.git('commit', '-m', 'Commit 0')
    repo.git('push', '--set-upstream', 'origin', 'master', ssh_cmd=ssh_cmd)

    git_project.wait_assert_api_branch_titles({'master': 'Commit 0'})
    webdriver.refresh()
    assert git_project.name in webdriver.title

    # Mercurial SSH operation cleanly refused (see heptapod#517)
    hg_repo = HgRepo.init(tmpdir.join('hg_repo'))
    code, _out, err = hg_repo.hg_unchecked('pull', '--ssh', ssh_cmd, ssh_url)
    assert code not in (0, 1)
    assert "not a Mercurial project" in err

    # let's do a commit with the API
    readme = "Important instructions"
    branch = 'master'
    proj.api_file_create('README.txt',
                         content=readme,
                         branch=branch,
                         commit_message='README')
    git_project.wait_assert_api_branch_titles({'master': 'README'})
    # identical update is not an error (for reference behaviour, see
    # heptapod#1988)
    proj.api_file_update('README.txt',
                         branch=branch,
                         start_branch=branch,
                         content=readme,
                         commit_message="README no-op update",
                         )

    repo.git('pull', ssh_cmd=ssh_cmd)
    assert repo_path.join('README.txt').read() == "Important instructions"
    # later on we'll check the full log.
    assert repo_path.join('foo').read() == "Hey this is in Git!\n"

    # HTTP operations

    clone_path = tmpdir.join('clone')
    http_url = git_project.owner_basic_auth_url
    clone = GitRepo.clone(http_url, clone_path)
    assert clone_path.join('README.txt').read() == "Important instructions"
    clone_path.join('foo').write("Tired of foo!")
    clone.git('add', 'foo')
    clone.git('commit', '-m', 'Commit in clone')
    clone.git('push')

    git_project.wait_assert_api_branch_titles({'master': 'Commit in clone'})

    # Pulling new commit in original repo (over SSH) for correctness assertion
    repo.git('pull', ssh_cmd=ssh_cmd)
    assert repo_path.join('foo').read() == "Tired of foo!"

    # Web UI is healthy with new commits
    webdriver.get(git_project.url)
    assert_webdriver_not_error(webdriver)

    # repository drop-down menu
    def get_menu():
        return {
            i.lower()
            for i in git_project.webdriver_repo_new_content_menu(refresh=True)
        }

    menu = get_menu()
    if 'new branch' not in menu:
        # the two groups are rendered independently, try again
        menu = get_menu()

    assert 'new branch' in menu
    assert 'new tag' in menu


def prepare_mr_source_branch(repo,
                             with_ci=False,
                             needing_rebase=True,
                             push_opts=(),
                             src_remote='origin'):
    """Prepare a source branch

    This is meant to be very close to what `prepare_topic()` does in the
    Mercurial case.

    :param src_remote_url: name of remote to push the source branch to. The
      ``origin```default value matches the case where source and target
      projects are the same.

    Graph after preparation if needing_rebase is True::

        * commit f6d284cc (HEAD -> antelope)
        | Author: Test Git <testgit@heptapod.test>
        | Date:   Thu Oct 29 13:08:46 2020 +0100
        |
        |     Même une antilope !
        |
        | * commit 8e1c7bbb (origin/master, master)
        |/  Author: Test Git <testgit@heptapod.test>
        |   Date:   Thu Oct 29 13:08:37 2020 +0100
        |
        |      Even a horse!
        |
        * commit 7bd79271
          Author: Test Git <testgit@heptapod.test>
          Date:   Thu Oct 29 13:08:31 2020 +0100

               Initial sentence

    """
    source_branch = 'antelope'
    repo.path.join('kitten').write("A lion is stronger than a kitten\n")
    if with_ci:
        # let's not depend on auto-devops (JSON is a subset of YaML)
        ci_config = dict(job=dict(script=["grep lion antelope"]))
        repo.path.join('.gitlab-ci.yml').write(json.dumps(ci_config))
        repo.git('add', '.gitlab-ci.yml')
    repo.git('add', 'kitten')
    repo.git('commit', '-m', 'Initial sentence')
    repo.git('branch', source_branch)
    if needing_rebase:
        repo.path.join('horse').write("A lion is stronger than a horse\n")
        repo.git('add', 'horse')
        repo.git('commit', '-m', "Even a horse!")
    repo.git('push', '--set-upstream', 'origin', 'master')
    repo.git('checkout', source_branch)

    repo.path.join('antelope').write("A lion is stronger than an antelope\n")
    repo.git('add', 'antelope')
    repo.git('commit', '-m', "Même une antilope !")
    print("Graph after preparation of source branch:")
    print(repo.graphlog())

    cmd = ['push']
    for push_opt in push_opts:
        cmd.append('-o')
        cmd.append(push_opt)
    cmd.extend(('--set-upstream', src_remote, 'antelope'))

    # using git_unchecked because we need stderr
    code, out, err = repo.git_unchecked(*cmd)
    assert code == 0
    if src_remote == 'origin' and 'merge_request.create' not in push_opts:
        # TODO investigate proper conditions for MR creation prompt
        # in forks
        assert "create a merge request for %s" % source_branch in err
    return source_branch


def test_mergerequest_api_explicit_merge_message(git_project_with_runner,
                                                 tmpdir):
    """Accepting the MR via API with an explicit merge changeset.

    see `test_merge_requests.test_mergerequest_api()` for relevance of API
    call for testing. In the Git case, we don't worry too much about the
    push protocol (HTTP or SSH), the low level side of it being handled
    by test_basic above, and the Git hooks calls being unchanged compared
    to GitLab. What matters is the Rails logic that is triggered by
    those hooks.
    """
    proj, runner = git_project_with_runner

    default_url = proj.owner_basic_auth_url
    repo = GitRepo.init(tmpdir.join('repo'),
                        default_url=default_url)
    src_branch = prepare_mr_source_branch(repo, with_ci=True)
    head_sha = repo.sha('refs/heads/' + src_branch)  # needs ambiguity lift
    mr = MergeRequest.api_create(proj, src_branch, target_branch='master')

    jobs = runner.wait_assert_jobs(2)
    assert set(job['git_info']['ref']
               for job in jobs) == {'master', 'antelope'}

    mr.api_accept()
    repo.git('pull', '--all')
    print("Graph after API merge:")
    print(repo.graphlog())

    log = repo.git('log', 'origin/master', '--oneline')
    titles = {l.split(' ', 1)[1] for l in log.splitlines()}
    assert titles == {
        "Merge branch 'antelope' into 'master'",
        "Même une antilope !",
        "Even a horse!",
        "Initial sentence",
    }

    mr.assert_commit_link("Même une antilope !", head_sha)

    # there's a CI job for the target
    job = runner.wait_assert_one_job()
    vcs_info = job['git_info']
    assert vcs_info['ref'] == 'master'
    assert vcs_info['repo_type'] == 'git'
    assert vcs_info['sha'] == repo.sha('origin/master')
    assert vcs_info.get('hgsha') is None


def test_mergerequest_api_conflict(git_project, tmpdir):
    """Testing API responses in case of conflict.

    This is useful to check we do not change GitLab behaviour (by comparing
    across revisions or even by running against pure GitLab) and to compare
    Mercurial responses with Git responses.
    """
    proj = git_project

    default_url = proj.owner_basic_auth_url
    repo = GitRepo.init(tmpdir.join('repo'),
                        default_url=default_url)
    src_branch = prepare_mr_source_branch(repo, with_ci=True)

    # baking the conflict
    repo.git('checkout', src_branch)
    repo.path.join('horse').write("You meant a zebra?")
    repo.git('add', 'horse')
    repo.git('commit', '-m', "Conflict")
    repo.git('push')

    mr = MergeRequest.api_create(proj, src_branch, target_branch='master')

    mr.wait_assert(lambda info: info.get('merge_status') == 'cannot_be_merged')

    resp = mr.api_accept(check_merged=False, wait_mergeability=False)

    # see doc/api/merge_requests.md
    assert resp.status_code == 422


@suitable.prod_server
def test_mergerequest_cli(git_project_with_runner, tmpdir):
    """Accepting the MR via a manual push, with an explicit merge changeset.
    """
    proj, runner = git_project_with_runner

    default_url = proj.owner_basic_auth_url
    repo = GitRepo.init(tmpdir.join('repo'),
                        default_url=default_url)
    src_branch = prepare_mr_source_branch(repo, with_ci=True)
    jobs = runner.wait_assert_jobs(2)
    assert set(job['git_info']['ref']
               for job in jobs) == {'master', 'antelope'}

    mr = MergeRequest.api_create(proj, src_branch, target_branch='master')

    repo.git('checkout', 'master')
    repo.git('merge', '-m', "merged 'antelope manually", 'antelope')
    print("Graph after CLI merge:")
    print(repo.graphlog())

    repo.git('push', 'origin', 'master')
    mr.wait_assert_merged(check_source_branch_removal=False)

    # there's a CI job for the target
    job = runner.wait_assert_one_job()
    vcs_info = job['git_info']
    assert vcs_info['ref'] == 'master'
    assert vcs_info['repo_type'] == 'git'
    assert vcs_info['sha'] == repo.sha('origin/master')
    assert vcs_info.get('hgsha') is None


@parametrize('fork_method', ('api', 'webdriver'))
def test_fork_mergerequest_api_explicit_merge_message(
        git_project, additional_user, tmpdir, fork_method):
    """Accepting MR done from a fork via API with an explicit merge changeset.
    """
    proj = git_project
    proj.grant_member_access(user=additional_user,
                             level=ProjectAccess.REPORTER)

    default_url = proj.owner_basic_auth_url
    repo = GitRepo.init(tmpdir.join('repo'), default_url=default_url)
    repo.path.join('foo').write("Hey this is in Git!\n")
    repo.git('add', 'foo')
    repo.git('commit', '-m', 'Commit 0')
    repo.git('push', '--set-upstream', 'origin', 'master')

    if fork_method == 'api':
        fork_meth = git_project.api_fork
    else:
        fork_meth = git_project.webdriver_fork

    with fork_meth(user=additional_user) as fork:
        repo.git('remote', 'add', 'fork', fork.owner_basic_auth_url)
        src_branch = prepare_mr_source_branch(repo,
                                              with_ci=True,
                                              src_remote='fork')
        head_sha = repo.sha('refs/heads/' + src_branch)  # with ambiguity lift
        mr = MergeRequest.api_create(fork, src_branch,
                                     target_project=proj,
                                     target_branch='master')

        mr.api_accept()
        mr.wait_assert_merged(check_source_branch_removal=False)

        repo.git('fetch', 'origin', 'master')
        print("Graph after API merge:")
        print(repo.graphlog())

        log = repo.git('log', 'origin/master', '--oneline')
        titles = {l.split(' ', 1)[1] for l in log.splitlines()}
        assert titles == {
            "Merge branch 'antelope' into 'master'",
            "Même une antilope !",
            "Even a horse!",
            "Initial sentence",
            "Commit 0",
        }

        # Commit list is correct (wouldn't work after deletion of fork)
        mr.assert_commit_link("Même une antilope !", head_sha)


def test_export_import(git_project, tmpdir):
    proj = git_project

    repo = prepare_import_source_git(proj, tmpdir)[0]

    tarball = BytesIO()
    git_project.api_export(tarball, timeout_factor=3)

    tarball.seek(0)
    with Project.api_import_tarball(
            proj.heptapod,
            proj.owner,
            unique_name('test_import'),
            tarball,
    ) as imported:
        assert imported.vcs_type == git_project.vcs_type

        imported.wait_assert_api_branch_titles({'master': 'Commit 0'})
        clone = GitRepo.clone(imported.owner_basic_auth_url,
                              tmpdir / 'imported-clone')
        assert clone.sha('master') == repo.sha('master')


def test_mergerequest_auto_create(git_project, tmpdir):
    proj = git_project

    default_url = proj.owner_basic_auth_url
    repo = GitRepo.init(tmpdir.join('repo'),
                        default_url=default_url)
    prepare_mr_source_branch(repo, push_opts=[
        'merge_request.create',
        'merge_request.title=Automatic creation',
        'merge_request.description=By push option',
    ])
    # ideally iid should be parsable from the push message, but
    # we're pretty sure of it anyway
    mr = MergeRequest(proj, 1)
    mr_info = mr.wait_assert(
        lambda info: (info is not None
                      and info['state'] == 'opened'
                      and info['merge_status'] == 'can_be_merged'
                      ))
    assert mr_info['source_branch'] == 'antelope'
    assert mr_info['target_branch'] == 'master'
    assert mr_info['title'] == 'Automatic creation'
    assert mr_info['description'] == 'By push option'

    # make sure that a single push option is still well understood
    # (removed an Array.wrap() on the Rails side in the `Gitlab::PushOptions`
    # class)
    repo.path.join('antelope').write("Last minute changen")
    repo.git('commit', '-am', "No more antelope!")
    repo.git('push', 'origin', 'antelope', '-o', 'ci.skip')


def test_webdriver_import(git_project, tmpdir):
    source_proj = git_project

    # making source_project public (easier to import, alhough passing of
    # credentials could also be tested).
    assert source_proj.api_edit(visibility='public').status_code == 200

    repo, external_url = prepare_import_source_git(git_project, tmpdir)

    with Project.webdriver_import_url(
            heptapod=git_project.heptapod,
            user=git_project.owner_user,
            project_name=unique_name('test_import_git'),
            url=external_url,
            wait_import_url_validation=True,
            vcs_type='git',
    ) as imported_proj:
        clone = GitRepo.clone(imported_proj.owner_basic_auth_url,
                              tmpdir / 'imported-clone')
        assert clone.sha('master') == repo.sha('master')


def test_webdriver_project_settings(git_project):
    proj = git_project
    proj.webdriver_update_merge_request_settings('ff')
    assert proj.api_get_field('merge_method') == 'ff'

    driver = proj.webdriver_get_settings_page('ci_cd')
    page = driver.page_source
    assert 'hg pull' not in page
    assert 'hg clone' not in page
    assert 'git fetch' in page
    assert 'git clone' in page


def xtest_webdriver_import_errors(public_project, tmpdir):
    """Test the outcome of some import errors.

    This is testing Git behaviour, hence both to check that
    upstream did not change its and that we did not break it. Both
    can happen and only failure investigation on precise run context can
    make the difference.
    """
    heptapod = public_project.heptapod
    src_repo, src_url = prepare_import_source_hg(public_project, tmpdir,
                                                 tweak_hgrc=False)
    user = heptapod.get_user('test_basic')

    with Project.webdriver_import_url(
            heptapod,
            user=user,
            project_name=unique_name('import_errors'),
            url=src_url,
            check_success=False,
            # here comes the error:
            vcs_type='git',
    ) as project:
        info = project.api_get_info()
        assert info['import_status'] == 'failed'
        expected_msg = "not a valid HTTP Git repository"
        assert expected_msg in info['import_error']

        error_title, error_body = project.webdriver_import_errors()
        assert "could not be imported" in error_title
        assert expected_msg in error_body

        # As of GitLab 15.11, there does not seem to be an API endpoint
        # that makes the distinction between empty repository and no
        # repository.
        project.webdriver_assert_no_repo(check_buttons=True)
