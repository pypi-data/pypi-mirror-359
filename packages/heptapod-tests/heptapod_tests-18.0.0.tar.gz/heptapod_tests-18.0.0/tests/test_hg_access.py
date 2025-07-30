"""Various permission related tests that don't fit elsewhere."""

from heptapod_tests.hg import LocalRepo


def test_deploy_token(test_project, public_project, tmpdir):
    repo_path = tmpdir.join('repo1')

    repo = LocalRepo.init(repo_path)
    repo_path.join('foo').write('foo0')
    repo.hg('commit', '-Am', "Commit 0")
    repo.hg('push', test_project.owner_basic_auth_url)

    clone = LocalRepo.init(tmpdir.join('repo2'))

    token1 = token2 = None

    # a deploy token for the *other* project does not grant clone permission
    token1 = public_project.api_create_deploy_token('test_token_1')
    clone.assert_hg_failure(
        'pull', test_project.deploy_token_url(token1),
        error_message_expectations='authorization failed')

    token2 = test_project.api_create_deploy_token('test_token_2')
    clone.hg('pull', test_project.deploy_token_url(token2))
    log = clone.hg('log', '-T', '{desc}:{phase}\n')
    assert log.splitlines() == ['Commit 0:public']
