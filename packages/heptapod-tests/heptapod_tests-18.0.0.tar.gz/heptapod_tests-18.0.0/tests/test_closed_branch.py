import re

from heptapod_tests.hg import LocalRepo


def test_push_branch_then_close(test_project, tmpdir):
    repo_path = tmpdir.join('repo1')

    # Minimal repo with two branches and one root
    repo = LocalRepo.init(repo_path,
                          default_url=test_project.owner_basic_auth_url)
    repo_path.join('foo').write('foo0')
    repo.hg('commit', '-Am', "Commit 0")
    repo_path.join('foo').write('foo1')
    repo.hg('commit', '-Am', "Commit 1")
    repo.hg('up', '0')
    repo.hg('branch', 'other')
    repo_path.join('foo').write("other")
    repo.hg('commit', '-m', "Commit 2")
    print(repo.graphlog())
    repo.hg('push')

    assert test_project.api_branch_titles() == {
        'branch/default': 'Commit 1',
        'branch/other': 'Commit 2',
    }

    repo.hg('commit', '-m', "Closing branch `other`", '--close-branch')
    repo.hg('push')

    test_project.wait_assert_api_branch_titles({'branch/default': 'Commit 1'})


def test_close_default_branch(test_project, tmpdir):
    """Closing default branch behaves according to project's VCS type

    - On `hg-git` projects, it shouldn't crash, and has no consequences on
      Git
    - on native projects, it must be refused by Heptapod
    """
    repo_path = tmpdir.join('repo1')

    # Minimal repo with two branches and one root
    repo = LocalRepo.init(repo_path,
                          default_url=test_project.owner_basic_auth_url)
    repo_path.join('foo').write('foo0')
    repo.hg('commit', '-Am', "Commit 0")
    repo_path.join('foo').write('foo1')
    repo.hg('commit', '-Am', "Commit 1")
    repo.hg('push')

    assert test_project.api_default_branch() == 'branch/default'

    repo.hg('commit', '-m', "Closing branch `default`", '--close-branch')
    repo.assert_hg_failure(
        'push',
        error_message_expectations=re.compile('close.*default branch')
    )
    assert test_project.api_branch_titles() == {'branch/default': 'Commit 1'}


def test_push_closed_branch(test_project, tmpdir):
    """Pushing closed branches in one go."""
    repo_path = tmpdir.join('repo1')

    # Minimal repo with two branches and one root
    repo = LocalRepo.init(repo_path,
                          default_url=test_project.owner_basic_auth_url)
    repo_path.join('foo').write('foo0')
    repo.hg('commit', '-Am', "Commit 0")
    repo_path.join('foo').write('foo1')
    repo.hg('commit', '-Am', "Commit 1")
    repo.hg('up', '0')
    repo.hg('branch', 'other')
    repo_path.join('foo').write("other")
    repo.hg('commit', '-m', "Commit 2")
    repo.hg('commit', '-m', "Closing branch `other`", '--close-branch')
    print(repo.graphlog())
    repo.hg('push')

    assert test_project.api_branch_titles() == {
        'branch/default': 'Commit 1',
    }
