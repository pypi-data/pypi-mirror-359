import subprocess
from heptapod_tests.hg import LocalRepo


def test_public(public_project, tmpdir):
    """
    Push two changesets, one being a draft, confirm their arrival and phases
    """
    repo_path = tmpdir.join('repo1')

    repo = LocalRepo.init(repo_path,
                          default_url=public_project.owner_basic_auth_url)
    repo_path.join('foo').write('foo0')
    repo.hg('commit', '-Am', "Commit 0")
    repo.hg('phase', '-p', ".")
    repo_path.join('bar').write('bar0')
    repo.hg('commit', '-Am', "Commit 1")
    repo.hg('topic', 'test-topic')
    repo_path.join('baz').write('baz0')
    repo.hg('commit', '-Am', "Commit 2")
    repo.hg('push')

    clone = LocalRepo.clone(public_project.url, tmpdir.join('repo2'))
    log = clone.hg('log', '-r', 'all()', '-T', '{desc}:{phase}\n')
    assert log.splitlines() == ['Commit 0:public',
                                'Commit 1:public',
                                'Commit 2:draft'
                                ]
    git_clone = str(tmpdir.join('git_clone'))
    for url in (public_project.url, public_project.url + '.git'):
        assert subprocess.call(['git', 'clone', url, git_clone]) != 0
