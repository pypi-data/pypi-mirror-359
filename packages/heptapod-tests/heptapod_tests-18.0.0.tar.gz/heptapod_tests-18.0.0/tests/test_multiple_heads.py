from heptapod_tests.hg import LocalRepo


def test_push_multiple_heads_merge(test_project, tmpdir):
    repo_path = tmpdir.join('repo1')
    owner_url = test_project.owner_basic_auth_url

    # a first public changeset, pushed as the owner
    repo = LocalRepo.init(repo_path)
    repo_path.join('foo').write('foo0')
    repo.hg('commit', '-Am', "Commit 0")
    repo.hg('push', owner_url)

    # first head on default branch
    repo_path.join('foo').write('foo1')
    repo.hg('commit', '-Am', "Head 1")

    # second head on default branch (easy to merge for later test)
    repo.hg('update', '0')
    repo_path.join('bar').write('bar')
    repo.hg('commit', '-Am', "Head 2")

    print(repo.graphlog())

    # by default, pushing multiple heads is forbidden
    repo.assert_hg_failure(
        'push', '-f', owner_url,
        error_message_expectations=('abort', 'rejecting multiple heads'))
    # let's allow it
    test_project.api_hgrc_set(inherit=True, allow_multiple_heads=True)

    repo.hg('push', '-f', owner_url)

    heads_titles = {'Head 1', 'Head 2'}
    test_project.wait_assert_api_branches(
        lambda branches: (
            len(branches) == 3
            and branches['branch/default']['commit']['title'] in heads_titles
            and set(info['commit']['title']
                    for name, info in branches.items()
                    if name.startswith('wild/')) == heads_titles
        ))

    # and let's get back to the normal case by merging those heads
    merge_msg = "Merging wild heads"
    repo.hg('merge')
    repo.hg('commit', '-m', merge_msg)
    repo.hg('push', owner_url)

    test_project.wait_assert_api_branches(
        lambda branches: (
            len(branches) == 1
            and branches['branch/default']['commit']['title'] == merge_msg
        )
    )


def test_push_multiple_heads_with_branch(test_project, tmpdir):
    """Linear branch history and and multiple heads in a single push.

    This is the extreme case in which the 'branch/default' GitLab branch
    wouldn't even exist if we refused to account for the linear history.
    In other words, this is what's explained in heptapod#101
    """
    test_project.api_hgrc_set(inherit=True, allow_multiple_heads=True)

    repo_path = tmpdir.join('repo1')
    owner_url = test_project.owner_basic_auth_url

    # a first public changeset, pushed as the owner
    repo = LocalRepo.init(repo_path)
    repo_path.join('foo').write('foo0')
    repo.hg('commit', '-Am', "Commit 0")

    # first head on default branch
    repo_path.join('foo').write('foo1')
    repo.hg('commit', '-Am', "Head 1")

    # second head on default branch
    repo.hg('update', '0')
    repo_path.join('bar').write('bar')
    repo.hg('commit', '-Am', "Head 2")

    print(repo.graphlog())

    repo.hg('push', '-f', owner_url)

    branches = test_project.api_branches()
    assert len(branches) == 3
    heads_titles = {'Head 1', 'Head 2'}
    assert branches['branch/default']['commit']['title'] in heads_titles
    assert set(info['commit']['title']
               for name, info in branches.items()
               if name.startswith('wild/')) == heads_titles


def test_push_multiple_heads_switch_branch(test_project, tmpdir):
    """Multiple heads, with one having a child on another branch."""
    test_project.api_hgrc_set(inherit=True, allow_multiple_heads=True)

    repo_path = tmpdir.join('repo1')
    # a first public changeset, pushed as the owner
    repo = LocalRepo.init(repo_path,
                          default_url=test_project.owner_basic_auth_url)
    repo_path.join('foo').write('foo0')
    repo.hg('commit', '-Am', "Commit 0")
    repo.hg('push')

    # first head on default branch
    repo_path.join('foo').write('foo1')
    repo.hg('commit', '-Am', "Head 1")

    # second head on default branch (easy to merge for later test)
    repo.hg('update', '0')
    repo_path.join('bar').write('bar')
    repo.hg('commit', '-Am', "Head 2")

    print(repo.graphlog())

    repo.hg('push', '-f')

    branches = test_project.api_branches()
    assert len(branches) == 3
    heads_titles = {'Head 1', 'Head 2'}
    assert branches['branch/default']['commit']['title'] in heads_titles
    assert set(info['commit']['title']
               for name, info in branches.items()
               if name.startswith('wild/')) == heads_titles

    repo.hg('branch', 'other')
    repo_path.join('foo').write("on other branch")
    repo.hg('commit', '-m', 'On other')
    repo.hg('push', '--new-branch')

    branches = test_project.wait_assert_api_branches(
        lambda branches: len(branches) == 4
    )
    heads_titles = {'Head 1', 'Head 2'}
    assert branches['branch/default']['commit']['title'] in heads_titles
    assert branches['branch/other']['commit']['title'] == 'On other'
    assert set(info['commit']['title']
               for name, info in branches.items()
               if name.startswith('wild/')) == heads_titles

    # now let's add a topic on top of one of those wild 'default' heads
    repo.hg('up', '1')
    assert repo.hg('branch').strip() == 'default'  # to be sure
    repo.hg('topic', 'zzetop')
    repo_path.join('foo').write("on topic")
    repo.hg('commit', '-m', 'On topic')
    print(repo.graphlog())
    repo.hg('push')

    branches = test_project.wait_assert_api_branches(
        lambda branches: set(b for b in branches
                             if not b.startswith('wild/')
                             ) == {'branch/default',
                                   'branch/other',
                                   'topic/default/zzetop'
                                   },
    )
    assert set(info['commit']['title']
               for name, info in branches.items()
               if name.startswith('wild/')) == heads_titles
    assert branches['branch/default']['commit']['title'] in heads_titles
    assert branches['branch/other']['commit']['title'] == 'On other'
    assert branches['topic/default/zzetop']['commit']['title'] == 'On topic'


def test_push_multiple_closed_heads(test_project, tmpdir):
    repo_path = tmpdir.join('repo1')
    # a first public changeset, pushed as the owner
    repo = LocalRepo.init(repo_path,
                          default_url=test_project.owner_basic_auth_url)
    repo_path.join('foo').write('foo0')
    repo.hg('commit', '-Am', "Commit 0")
    repo.hg('push')

    # first head on default branch
    repo_path.join('foo').write('foo1')
    repo.hg('commit', '-Am', "Head 1")

    # second head on default branch will be closed
    repo.hg('update', '0')
    repo_path.join('bar').write('bar')
    repo.hg('commit', '-Am', "Head 2")
    repo.hg('commit', '--close-branch', '-m', "closing Head 2")
    print(repo.graphlog())

    # it's quite possible that in the future we'll forbid pushing
    # *new* closed heads. The point of this test is to make sure that
    # if closed heads should not be in the way of pushing children of the
    # one that's not closed.
    test_project.api_hgrc_set(inherit=True, allow_multiple_heads=True)

    repo.hg('push', '-f')
    branches = test_project.api_branches()
    assert len(branches) == 1
    assert branches['branch/default']['commit']['title'] == 'Head 1'

    # let's forbid multiple heads again, and be sure of that
    test_project.api_hgrc_set(inherit=True, allow_multiple_heads=False)

    repo.hg('update', '0')
    repo_path.join('bar').write('baz')
    repo.hg('commit', '-Am', "Head 3")
    repo.assert_hg_failure(
        'push', '-f',
        error_message_expectations=('abort', 'rejecting multiple heads'))

    # now, pushing children of the non closed head should work
    repo.hg('up', '1')
    repo_path.join('bar').write('something else')
    repo.hg('commit', '-Am', 'follow-up')
    repo.hg('push', '-r', '.')

    test_project.wait_assert_api_branches(
        lambda branches: (
            len(branches) == 1
            and branches['branch/default']['commit']['title'] == 'follow-up'
        )
    )


def test_push_multiple_heads_topic_merge(test_project, tmpdir):
    """Same as test_push_multiple_heads_merge, within a topic."""
    repo_path = tmpdir.join('repo1')
    owner_url = test_project.owner_basic_auth_url

    # a first public changeset, pushed as the owner
    repo = LocalRepo.init(repo_path)
    repo_path.join('foo').write('foo0')
    repo.hg('commit', '-Am', "Commit 0")
    repo.hg('push', owner_url)

    # first head on topic
    repo.hg('topic', 'zz')
    repo_path.join('foo').write('foo1')
    repo.hg('commit', '-Am', "Head 1")

    # second head on topic (easy to merge for later test)
    repo.hg('update', 's0')
    repo_path.join('bar').write('bar')
    repo.hg('commit', '-Am', "Head 2")

    print(repo.graphlog())

    # by default, pushing multiple heads is forbidden, also on topics
    repo.assert_hg_failure(
        'push', '-f', owner_url,
        error_message_expectations=('abort', 'rejecting multiple heads'))

    # let's allow it
    test_project.api_hgrc_set(inherit=True, allow_multiple_heads=True)

    repo.hg('push', '-f', owner_url)

    branches = test_project.api_branches()
    assert len(branches) == 4
    heads_titles = {'Head 1', 'Head 2'}
    assert branches['branch/default']['commit']['title'] == 'Commit 0'
    assert set(info['commit']['title']
               for name, info in branches.items()
               if name.startswith('wild/')) == heads_titles
    assert branches['topic/default/zz']['commit']['title'] in heads_titles

    # and let's get back to the normal case by merging those heads
    merge_msg = "Merging heads of topic"
    repo.hg('merge')
    repo.hg('commit', '-m', merge_msg)
    repo.hg('push', owner_url)

    branches = test_project.wait_assert_api_branches(
        lambda branches: set(branches) == {'branch/default',
                                           'topic/default/zz'})
    assert branches['topic/default/zz']['commit']['title'] == merge_msg
    assert branches['branch/default']['commit']['title'] == 'Commit 0'
