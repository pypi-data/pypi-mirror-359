from heptapod_tests.hg import LocalRepo
from heptapod_tests.project import (
    branch_title,
)


def test_push_bookmarks_default_branch(test_project, tmpdir):
    repo_path = tmpdir.join('repo1')
    url = test_project.owner_basic_auth_url

    repo = LocalRepo.init(repo_path)
    # As usual, let's make a first public changeset
    repo_path.join('foo').write('foo0')
    repo.hg('commit', '-Am', "Commit 0")
    repo.hg('phase', '-p', ".")
    repo.hg('push', url)

    repo_path.join('foo').write('foo1')
    repo.hg('commit', '-m', "Commit 1")
    repo.hg('bookmark', '-r', '.', 'book1')
    print(repo.graphlog())

    # Bookmarks should be forbidden by default
    repo.assert_hg_failure('push', '-B', 'book1', url,
                           error_message_expectations=('forbidden', 'book1'))

    # now let's allow bookmarks on non-topic changesets
    test_project.api_hgrc_set(inherit=True, allow_bookmarks=True)

    repo.hg('push', '-B', 'book1', url)
    branches = test_project.api_branches()
    # even though the 'default' named branch only has bookmarked heads,
    # the 'branch/default' GitLab branch should not be pruned, because it is
    # also GitLab's default branch (hence also the HEAD of the inner Git
    # repo)
    assert set(branches) == {'branch/default', 'book1'}
    assert branches['branch/default']['commit']['title'] == 'Commit 1'
    assert branches['book1']['commit']['title'] == 'Commit 1'

    # on the other hand, bookmarks on topics are still refused
    repo.hg('up', '0')
    repo_path.join('foo').write('foo3')
    repo.hg('topic', 'topbook')
    repo.hg('commit', '-m', "ontopic")
    repo.hg('bookmark', '-r', '.', 'book-on-top')

    # Bookmarks on topics are expected to be forbidden"
    repo.assert_hg_failure(
        'push', '-B', 'book-on-top', url,
        error_message_expectations=('topbook', 'book-on-top',
                                    repo.node('book-on-top')))

    # now let's try with a second bookmark on the same branch
    # (used to be a limitation of our modified hg-git)
    repo.hg('up', '0')
    repo_path.join('foo').write('foo2')
    repo.hg('commit', '-m', "Commit 2")
    repo.hg('bookmark', '-r', '.', 'book2')

    # it's also necessary to force-push
    repo.hg('push', '-f', '-B', 'book2', url)

    test_project.wait_assert_api_branches(
        lambda branches: (
            set(branches) == {'branch/default', 'book1', 'book2'}
            and branches['branch/default']['commit']['title'] == 'Commit 2'
            and branches['book1']['commit']['title'] == 'Commit 1'
            and branches['book2']['commit']['title'] == 'Commit 2'
        )
    )


def test_push_bookmarks_non_default_branch(test_project, tmpdir):
    repo_path = tmpdir.join('repo1')
    url = test_project.owner_basic_auth_url

    repo = LocalRepo.init(repo_path)
    # As usual, let's make a first public changeset
    repo_path.join('foo').write('foo default')
    repo.hg('commit', '-Am', "Commit on default")
    repo.hg('phase', '-p', ".")
    repo.hg('push', url)

    repo.hg('branch', 'other')
    repo_path.join('foo').write('foo branch')
    repo.hg('commit', '-m', "Commit 0")
    repo.hg('push', '--new-branch', url)
    # Just to be sure
    branches = test_project.api_branches()
    assert set(branches) == {'branch/default', 'branch/other'}

    repo_path.join('foo').write('foo1')
    repo.hg('commit', '-m', "Commit 1")
    repo.hg('bookmark', '-r', '.', 'book1')
    print(repo.graphlog())

    # Bookmarks are supposed to be forbidden by default"
    repo.assert_hg_failure('push', '-B', 'book1', url,
                           error_message_expectations='forbidden')

    # now let's allow bookmarks on non-topic changesets
    test_project.api_hgrc_set(inherit=True, allow_bookmarks=True)

    repo.hg('push', '-B', 'book1', url)

    # hg branch 'other' has no non bookmarked head, therefore the GitLab
    # branch 'branch/other' has been replaced by the bookmark.
    branches = test_project.wait_assert_api_branches(
        lambda branches: set(branches) == {'branch/default', 'book1'},
    )
    assert branches['branch/default']['commit']['title'] == 'Commit on default'
    assert branches['book1']['commit']['title'] == 'Commit 1'

    # on the other hand, bookmarks on topics are still refused
    repo.hg('up', '1')
    repo_path.join('foo').write('foo3')
    repo.hg('topic', 'topbook')
    repo.hg('commit', '-m', "ontopic")
    repo.hg('bookmark', '-r', '.', 'book-on-top')

    # Bookmarks on topics are expected to be forbidden"
    repo.assert_hg_failure(
        'push', '-B', 'book-on-top', url,
        error_message_expectations=('topbook', 'book-on-top',
                                    repo.node('book-on-top')))

    # now let's try with a second bookmark on the same branch
    # (used to be a limitation of our modified hg-git)
    repo.hg('up', '1')
    repo_path.join('foo').write('foo2')
    repo.hg('commit', '-m', "Commit 2")
    repo.hg('bookmark', '-r', '.', 'book2')

    # it's also necessary to force-push
    repo.hg('push', '-f', '-B', 'book2', url)

    # New bookmark is listed in GitLab branch, 'branch/other' isn't
    branches = test_project.wait_assert_api_branches(
        lambda branches: set(branches) == {'branch/default', 'book1', 'book2'},
    )
    assert branches['book1']['commit']['title'] == 'Commit 1'
    assert branches['book2']['commit']['title'] == 'Commit 2'

    # let's add a non bookmarked head and check that it becomes 'branch/other'
    # again
    repo.hg('up', '1')
    repo_path.join('foo').write('not a bookmark')
    repo.hg('commit', '-m', "Not bookmarked")
    # let's be sure 'book1' hasn't moved
    assert repo.hg('bookmarks', '-l', 'book1', '-T', '{rev}').strip() == '2'
    repo.hg('push', '-f', '-r', '.', url)

    branches = test_project.wait_assert_api_branches(
        lambda branches: set(branches) == {'branch/default', 'branch/other',
                                           'book1', 'book2'},
    )
    assert branches['book1']['commit']['title'] == 'Commit 1'
    assert branches['book2']['commit']['title'] == 'Commit 2'
    assert branches['branch/other']['commit']['title'] == 'Not bookmarked'


def test_implicit_move(test_project, tmpdir):
    repo_path = tmpdir.join('repo1')
    url = test_project.owner_basic_auth_url

    repo = LocalRepo.init(repo_path)
    # As usual, let's make a first public changeset
    repo_path.join('foo').write('foo default')
    repo.hg('commit', '-Am', "Commit on default")
    repo.hg('phase', '-p', ".")
    repo.hg('push', url)

    repo.hg('branch', 'other')
    repo_path.join('foo').write('foo branch')
    repo.hg('commit', '-m', "Commit 1")
    repo.hg('push', '--new-branch', url)
    # Just to be sure
    branches = test_project.api_branches()
    assert set(branches) == {'branch/default', 'branch/other'}

    repo_path.join('foo').write('foo1')
    repo.hg('commit', '-m', "Commit 1")
    repo.hg('bookmark', '-r', '.', 'book')
    print(repo.graphlog())

    test_project.api_hgrc_set(allow_bookmarks=True)
    repo.hg('push', '-B', 'book', url)
    branches = test_project.api_branch_titles()
    test_project.api_hgrc_set(allow_bookmarks=False)

    repo_path.join('foo').write('foo2')
    repo.hg('commit', '-m', "Commit 2")
    repo.hg('bookmark', '-r', '.', 'book')

    # notice how we dont explicitely push the bookmark
    repo.hg('push', url)

    # yet, it moved
    test_project.wait_assert_api_branches(
        lambda branches: branch_title(branches, 'book') == 'Commit 2',
    )

    # bookmark removal is possible and it restores the shadowed branch
    repo.hg('bookmark', '-d', 'book')
    out = repo.hg('push', '-B', 'book', url, expected_return_code=1)
    assert 'deleting remote bookmark book' in out
    test_project.wait_assert_api_branch_titles(
        {'branch/default': 'Commit on default',
         'branch/other': 'Commit 2',
         },
    )

    # now imagine a bookmark slides to the head of a branch
    # first, prepare it
    test_project.api_hgrc_set(allow_bookmarks=True)
    repo.hg('bookmark', '-r', '1', 'sliding')
    repo.hg('push', '-B', 'sliding', url, expected_return_code=1)
    test_project.api_hgrc_set(allow_bookmarks=False)

    # let's move it to the head of 'other'
    repo.hg('bookmark', '-r', 'other', 'sliding')
    repo.hg('push', '-B', 'sliding', url, expected_return_code=1)

    gl_branches = {
        'branch/default': 'Commit on default',
        'sliding': 'Commit 2',
        'branch/other': 'Commit 2',
    }

    test_project.wait_assert_api_branch_titles(gl_branches)

    if test_project.hg_native:
        # additional test to check that sliding to the head of
        # the GitLab default branch has no ill effects

        # verifying our assumptions
        assert test_project.api_default_branch() == 'branch/default'
        repo.hg('bookmark', '--force', '-r', 'default', 'sliding')
        repo.hg('push', '-B', 'sliding', url, expected_return_code=1)
        test_project.wait_assert_api_branch_titles(
            {
                'branch/default': 'Commit on default',
                'branch/other': 'Commit 2',
                'sliding': 'Commit on default'
            },
        )
