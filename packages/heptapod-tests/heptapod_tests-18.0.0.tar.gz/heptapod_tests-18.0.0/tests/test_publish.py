from heptapod_tests.access_levels import ProjectAccess
from heptapod_tests.hg import LocalRepo


def test_publish_perms(test_project, tmpdir):
    repo_path = tmpdir.join('repo1')
    owner_url = test_project.owner_basic_auth_url
    basic_user_url = test_project.basic_auth_url(user_name='test_basic')

    repo = LocalRepo.init(repo_path)
    repo_path.join('foo').write('foo0')
    repo.hg('commit', '-Am', "Commit 0")
    print(repo.graphlog())
    repo.hg('push', owner_url)

    # give basic user rights to the project
    test_project.grant_member_access(user_name='test_basic',
                                     level=ProjectAccess.DEVELOPER)

    # basic user now can push a draft changeset
    repo.hg('topic', 'zetop')
    repo_path.join('foo').write('foo1')
    repo.hg('commit', '-Am', "Commit 1")
    repo.hg('push', basic_user_url)

    # but can't publish
    repo.hg('phase', '-p', '.')
    repo.assert_hg_failure('push', basic_user_url,
                           error_message_expectations='not authorised '
                           'to publish',
                           stderr_expectations='abort')

    # OTOH, maintainers can push the publication
    test_project.grant_member_access(user_name='test_basic',
                                     level=ProjectAccess.MAINTAINER)
    repo.hg('push', basic_user_url, expected_return_code=1)

    clone = LocalRepo.clone(owner_url, tmpdir.join('repo2'))
    log = clone.hg('log', '-T', '{desc}:{phase}:{topic}\n')
    print(clone.graphlog())
    assert log.splitlines() == ['Commit 1:public:',
                                'Commit 0:public:']
