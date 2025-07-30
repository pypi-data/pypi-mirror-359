"""These tests are for `hg prune` done client-side

This is not about pruning GitLab branches as a result of pushes.
"""
from heptapod_tests.hg import LocalRepo


def test_prune_inside_topic(test_project, tmpdir):
    """
    After pruning the first changeset of a series, we should be able to push

    It's possible that at some point, we're gonna enforce by default
    be accepted on the server, and this will have to be deactivated.
    """
    repo_path = tmpdir.join('repo')
    url = test_project.owner_basic_auth_url
    repo = LocalRepo.init(repo_path)
    repo_path.join('foo').write('foo0')
    repo.hg('commit', '-Am', "Commit 0")
    repo.hg('phase', '-p', ".")
    repo.hg('topic', 'some_topic')

    repo_path.join('foo').write('foo1')
    repo.hg('commit', '-Am', "Commit 1")

    repo_path.join('foo').write('foo2')
    repo.hg('commit', '-Am', "Commit 2")
    repo.hg('push', url)

    repo.hg('prune', '-r', 's1')
    # we don't need to force for pushing an orphan changeset: it's already in
    # the remote.
    repo.hg('push', url, expected_return_code=1)

    # now reclone and check hg log
    clone = LocalRepo.clone(url, tmpdir.join('clone'))
    log = clone.hg('log', '-T', "{phase}:{troubles}:{obsolete}:{topic}\n")
    assert log.splitlines() == [
        'draft:orphan::some_topic',
        'draft::obsolete:some_topic',
        'public:::',
    ]


def test_prune_whole_topic(test_project, tmpdir):
    """
    After pruning a topic, we should be able to push
    """
    repo_path = tmpdir.join('repo')
    url = test_project.owner_basic_auth_url
    repo = LocalRepo.init(repo_path)
    repo_path.join('foo').write('foo0')
    repo.hg('commit', '-Am', "Commit 0")
    repo.hg('phase', '-p', ".")
    repo.hg('push', url)
    repo.hg('topic', 'some_topic')

    repo_path.join('foo').write('foo1')
    repo.hg('commit', '-Am', "Commit 1")

    repo.hg('push', url)

    repo.hg('prune', '-r', '.')
    repo.hg('push', url, expected_return_code=1)

    # now reclone and check hg log
    clone = LocalRepo.clone(url, tmpdir.join('clone'))
    log = clone.hg('log', '-T',
                   "{phase}:{troubles}:{obsolete}:{topic}:{desc}\n")
    assert log.splitlines() == ['public::::Commit 0']


def test_prune_topic_successor_other_topic(test_project, tmpdir):
    """
    After pruning a topic, we should be able to push
    """
    repo_path = tmpdir.join('repo')
    url = test_project.owner_basic_auth_url
    repo = LocalRepo.init(repo_path)
    repo_path.join('foo').write('foo0')
    repo.hg('commit', '-Am', "Commit 0")
    repo.hg('push', url)

    repo.hg('phase', '-p', ".")
    repo.hg('topic', 'topic1')

    repo_path.join('foo').write('foo1')
    repo.hg('commit', '-Am', "Commit 1")

    repo.hg('up', 'default')
    repo.hg('topic', 'topic2')
    repo_path.join('foo').write('foo2')
    repo.hg('commit', '-Am', "Commit 2")
    repo.hg('phase', '-p', '.')
    repo.hg('push', url)

    # can't use 'topic2' to access Commit 2 any more, it's been published
    # and is now the head of default.
    repo.hg('prune', '-r', 'topic1', '-s', 'default')
    repo.hg('push', url, expected_return_code=1)

    # now reclone and check hg log
    clone = LocalRepo.clone(url, tmpdir.join('clone'))
    log = clone.hg('log', '-T',
                   "{phase}:{troubles}:{obsolete}:{topic}:{desc}\n")
    assert log.splitlines() == ['public::::Commit 2',
                                'public::::Commit 0',
                                ]
