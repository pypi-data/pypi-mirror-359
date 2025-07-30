from heptapod_tests.access_levels import ProjectAccess
from heptapod_tests.git import LocalRepo as GitLocalRepo
from heptapod_tests.hg import LocalRepo

from . import suitable


def make_repo(tmpdir, name, topic_branch=None):
    repo_path = tmpdir.join(name)

    repo = LocalRepo.init(repo_path)
    repo_path.join('foo').write('foo0')
    repo.hg('commit', '-Am', "Commit 0")
    repo.hg('phase', '-p', ".")

    if topic_branch is not None:
        repo.hg('branch', topic_branch)
    repo.hg('topic', 'zetop')
    repo_path.join('foo').write('foo1')
    repo.hg('commit', '-Am', "Commit 1")
    return repo


def assert_is_clone_ok(repo):
    """Assert that a repo is a good clone of what `make_repo()` creates."""
    log = repo.hg('log', '-T', '{desc}:{phase}:{topic}\n')
    assert log.splitlines() == ['Commit 1:draft:zetop', 'Commit 0:public:']


def assert_pushed_repo(project, tmpdir, clone_name='clone'):
    """Check that a push with contents as provided by `make_repo()`.

    This is done by API calls and by cloning over HTTP, which is assumed
    to work, since we are testing SSH.
    """
    clone = LocalRepo.clone(project.owner_basic_auth_url,
                            tmpdir.join(clone_name))
    assert_is_clone_ok(clone)

    # now GitLab side:
    assert project.api_branch_titles() == {
        'branch/default': 'Commit 0',
        'topic/default/zetop': 'Commit 1',
    }


@suitable.prod_server
def test_owner_push_pull(test_project, tmpdir):
    repo = make_repo(tmpdir, 'repo1')
    ssh_cmd, ssh_url = test_project.owner_ssh_params
    repo.hg('push', '--ssh', ssh_cmd, ssh_url)
    assert_pushed_repo(test_project, tmpdir)

    # Testing that trailing slash is ignored (heptapod#151, heptapod#290)
    # and URL with / without .hg
    ssh_alt_url = ssh_url[:-3] if ssh_url.endswith('.hg') else ssh_url + '.hg'
    for name, url in (('main', ssh_url),
                      ('slash', ssh_url + '/'),
                      ('alt', ssh_alt_url),
                      ('alt_slash', ssh_alt_url + '/'),
                      ):
        ssh_clone = LocalRepo.init(tmpdir.join('ssh_clone_' + name))
        ssh_clone.hg('pull', '--ssh', ssh_cmd, url)
        assert_is_clone_ok(ssh_clone)

    # Cloning via Git should **not** be possible
    git_ssh_cmd, git_ssh_address = test_project.git_ssh_params(
        test_project.owner)
    GitLocalRepo.clone(git_ssh_address,
                       tmpdir.join('git_ssh_clone'),
                       expected_return_code=128,
                       ssh_cmd=git_ssh_cmd)


def test_permissions(test_project, tmpdir):
    # we'll need a named branch that is not protected on the GitLab side
    repo = make_repo(tmpdir, 'repo1')
    repo.hg('push', test_project.owner_basic_auth_url)

    ssh_cmd, ssh_url = test_project.ssh_params('test_basic')

    # at start, `test_basic` doesn't have access to test_project,
    # privately owner by `root`
    clone_path = tmpdir.join('user_clone')
    user_clone = LocalRepo.init(clone_path)
    user_clone.assert_hg_failure('pull', '--ssh', ssh_cmd, ssh_url,
                                 # that's GitLab policy
                                 stderr_expectations='could not be found')

    # let's give access and try pulling again
    # (REPORTER is the minimal access level to pull)
    basic_user = test_project.heptapod.users['test_basic']
    test_project.grant_member_access(user=basic_user,
                                     level=ProjectAccess.REPORTER)
    test_project.wait_assert_user_visible(basic_user)
    user_clone.hg('pull', '--ssh', ssh_cmd, ssh_url)
    assert_is_clone_ok(user_clone)

    # At the REPORTER level, one is not allowed to push over SSH
    clone_path.join('bar').write("in clone")
    user_clone.hg('up', 'default')
    user_clone.hg('branch', 'other')
    user_clone.hg('topic', 'user_topic')
    user_clone.hg('commit', '-Am', 'clone commit')

    user_clone.assert_hg_failure(
        'push', '--ssh', ssh_cmd, ssh_url,
        stdout_expectations="does not have write permission",
        # messages on stderr are the abort notice and an implementation
        # detail (hook)
    )

    # At the DEVELOPER level, however pushing on topics is allowed
    test_project.grant_member_access(user=basic_user,
                                     level=ProjectAccess.DEVELOPER)

    user_clone.hg('push', '--ssh', ssh_cmd, ssh_url)

    assert test_project.api_branch_titles() == {
        'branch/default': 'Commit 0',
        'topic/default/zetop': 'Commit 1',
        'topic/other/user_topic': 'clone commit',
    }

    # But still can't publish
    user_clone.hg('phase', '-p', 'user_topic')
    user_clone.assert_hg_failure(
        'push', '--ssh', ssh_cmd, ssh_url,
        error_message_expectations='not authorised to publish')

    # of course at the HG_PUBLISHER, it is possible to publish as long
    # as protected branch rules don't forbid it.
    test_project.grant_member_access(user=basic_user,
                                     level=ProjectAccess.HG_PUBLISHER)
    user_clone.hg('push', '--ssh', ssh_cmd, ssh_url,
                  expected_return_code=1)
    test_project.wait_assert_api_branches(
        lambda branches: 'topic/other/user_topic' not in branches)

    # …and even moreso at the MAINTAINER level
    test_project.grant_member_access(user=basic_user,
                                     level=ProjectAccess.HG_PUBLISHER)
    repo.path.join('foo').write('foo2')
    user_clone.hg('commit', '-Am', 'clone commit 2')
    user_clone.hg('push', '--publish', '-r', '.', '--ssh', ssh_cmd, ssh_url)
