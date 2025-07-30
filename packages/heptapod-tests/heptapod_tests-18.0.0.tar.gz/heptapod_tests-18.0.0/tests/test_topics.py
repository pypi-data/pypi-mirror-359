import pytest
from urllib.parse import parse_qs

from heptapod_tests.access_levels import ProjectAccess
from heptapod_tests.hg import LocalRepo

parametrize = pytest.mark.parametrize


@parametrize('pull_type', ('pull-rev', 'pull-full'))
def test_gate_topics(test_project, tmpdir, pull_type):
    """
    Clients without the topic extension won't get them unless explicitely
    """
    repo_path = tmpdir.join('repo1')
    url = test_project.owner_basic_auth_url

    repo = LocalRepo.init(repo_path)
    repo_path.join('foo').write('foo0')
    repo.hg('commit', '-Am', "Commit 0")
    repo.hg('phase', '-p', ".")
    repo.hg('topic', 'zetop')

    repo_path.join('foo').write('foo1')
    repo.hg('commit', '-Am', "Commit 1")
    topic_sha = repo.hg('log', '-r', '.', '-T', '{node}')
    repo.hg('push', url)

    # let's control what GitLab really sees
    assert test_project.api_branch_titles() == {
        'branch/default': 'Commit 0',
        'topic/default/zetop': 'Commit 1',
    }

    clone = LocalRepo.init(tmpdir.join('clone'))
    clone.hgrc_append_lines(("", "[extensions]", "topic=!"))
    clone.hg('pull', url)
    log = clone.hg('log', '-T', '{desc}:{phase}\n')
    assert log.splitlines() == ['Commit 0:public']
    # but requiring a topical changeset by its SHA with just the topic
    # extension (not evolve) works

    cmd = ['pull']
    if pull_type == 'pull-rev':
        cmd.extend(('-r', topic_sha))
    cmd .extend((url,
                 '--config', 'extensions.topic=',
                 '--config', 'extensions.evolve=!'))
    clone.hg(*cmd)
    log = clone.hg('log', '-T', '{desc}:{phase}\n')
    assert log .splitlines() == ['Commit 1:draft', 'Commit 0:public']


def test_push_topic_permission(test_project, tmpdir):
    """Even for topic changesets, DEVELOPER is the minimal perm to push.
    """
    repo_path = tmpdir.join('repo1')
    owner_url = test_project.owner_basic_auth_url
    basic_user_url = test_project.basic_auth_url(user_name='test_basic')

    # a first public changeset, pushed as the owner
    repo = LocalRepo.init(repo_path)
    repo_path.join('foo').write('foo0')
    repo.hg('commit', '-Am', "Commit 0")
    repo.hg('phase', '-p', ".")
    repo.hg('push', owner_url)

    repo.hg('topic', 'zetop')
    repo_path.join('foo').write('foo1')
    repo.hg('commit', '-Am', "Commit 1")

    # basic user is not member of the project, hence can't even see it
    repo.assert_hg_failure('push', basic_user_url, stderr_expectations='404')

    # basic user is Guest of the project
    test_project.grant_member_access(user_name='test_basic',
                                     level=ProjectAccess.GUEST)
    repo.assert_hg_failure('push', basic_user_url, stderr_expectations='403')

    # basic user is Reporter of the project
    test_project.grant_member_access(user_name='test_basic',
                                     level=ProjectAccess.REPORTER)
    repo.assert_hg_failure('push', basic_user_url, stderr_expectations='403')

    # finally basic user is Developer
    test_project.grant_member_access(user_name='test_basic',
                                     level=ProjectAccess.DEVELOPER)
    repo.hg('push', basic_user_url)

    # let's control what GitLab really sees
    assert test_project.api_branch_titles() == {
        'branch/default': 'Commit 0',
        'topic/default/zetop': 'Commit 1',
    }


def test_topic_rename(test_project, tmpdir):
    repo_path = tmpdir.join('repo1')
    url = test_project.owner_basic_auth_url

    repo = LocalRepo.init(repo_path)
    repo_path.join('foo').write('foo0')
    repo.hg('commit', '-Am', "Commit 0")
    repo.hg('phase', '-p', ".")
    repo.hg('push', url)  # avoid topic being default GitLab branch

    repo.hg('topic', 'zetop')

    repo_path.join('foo').write('foo1')
    repo.hg('commit', '-Am', "Commit 1")
    repo.hg('push', url)

    branches = test_project.api_branches()
    assert set(branches) == {'branch/default', 'topic/default/zetop'}
    assert branches['branch/default']['commit']['title'] == 'Commit 0'
    assert branches['topic/default/zetop']['commit']['title'] == 'Commit 1'

    repo.hg('topic', '-r', '.', 'newtopname')
    repo.hg('push', url)
    test_project.wait_assert_api_branches(
        lambda branches: (
            set(branches) == {'branch/default', 'topic/default/newtopname'}
            and branches['branch/default']['commit']['title'] == 'Commit 0'
            and (branches['topic/default/newtopname']['commit']['title']
                 == 'Commit 1')
        ))


def test_topic_rename_partial(test_project, tmpdir):
    """We don't want to prune a topic if it hasn't been fully renamed"""
    repo_path = tmpdir.join('repo1')
    url = test_project.owner_basic_auth_url

    repo = LocalRepo.init(repo_path)
    repo_path.join('foo').write('foo0')
    repo.hg('commit', '-Am', "Commit 0")
    repo.hg('phase', '-p', ".")
    repo.hg('push', url)  # avoid topic being default GitLab branch

    repo.hg('topic', 'zetop')

    repo_path.join('foo').write('foo1')
    repo.hg('commit', '-Am', "Commit 1")
    repo_path.join('foo').write('foo2')
    repo.hg('commit', '-Am', "Commit 2")
    repo.hg('push', url)

    branches = test_project.api_branches()
    assert set(branches) == {'branch/default', 'topic/default/zetop'}
    assert branches['branch/default']['commit']['title'] == 'Commit 0'
    assert branches['topic/default/zetop']['commit']['title'] == 'Commit 2'

    repo.hg('topic', '-r', '.', 'newtopname')
    repo.hg('push', url)
    branches = test_project.wait_assert_api_branches(
        lambda branches: set(branches) == {'branch/default',
                                           'topic/default/zetop',
                                           'topic/default/newtopname'},
    )
    assert branches['branch/default']['commit']['title'] == 'Commit 0'
    assert branches['topic/default/zetop']['commit']['title'] == 'Commit 1'
    assert (branches['topic/default/newtopname']['commit']['title']
            == 'Commit 2')


def test_only_topic_rename_simple(test_project, tmpdir):
    repo_path = tmpdir.join('repo1')
    url = test_project.owner_basic_auth_url

    repo = LocalRepo.init(repo_path)
    repo.hg('topic', 'zetop')
    repo_path.join('foo').write('foo0')
    repo.hg('commit', '-Am', "Commit 0")
    repo.hg('push', url)
    top1_gl_branch = 'topic/default/zetop'
    assert test_project.api_default_branch() == top1_gl_branch
    test_project.wait_assert_api_branches(
        lambda branches: set(branches) == {top1_gl_branch}
    )

    repo.hg('topic', '-r', '.', 'newtop')
    repo.hg('push', url, '-f')  # forcing because repo looks unrelated
    top2_gl_branch = 'topic/default/newtop'
    assert test_project.api_default_branch() == top2_gl_branch
    test_project.wait_assert_api_branches(
        lambda branches: top2_gl_branch in branches
    )

    out = repo.hg('push', '--pub', url, expected_return_code=1)
    assert test_project.api_default_branch() == 'branch/default'
    assert "Setting 'branch/default' as Heptapod default branch" in out

    # actual branch removal is guaranteed by a further push, but we
    # have to make sure the branches are not still protected
    for top in (top1_gl_branch, top2_gl_branch):
        test_project.api_ensure_branch_is_unprotected(top)
    repo_path.join('bar').write('some bar')
    repo.hg('top', '--clear')
    repo.hg('commit', '-Am', "Further work")
    repo.hg('push', url)

    test_project.wait_assert_api_branches(
        lambda branches: set(branches) == {'branch/default'}
    )
    assert test_project.api_default_branch() == 'branch/default'


def test_only_topic_rename_stacked(test_project, tmpdir):
    """Scenario for reproduction of heptapod#1716"""
    repo_path = tmpdir.join('repo1')
    url = test_project.owner_basic_auth_url

    repo = LocalRepo.init(repo_path)
    repo.hg('topic', 'dev')
    top1_gl_branch = 'topic/default/dev'
    repo_path.join('foo').write('foo0')
    repo.hg('commit', '-Am', "Commit 0")
    out = repo.hg('push', url)
    assert f"'{top1_gl_branch}' as Heptapod default branch" in out

    assert test_project.api_default_branch() == top1_gl_branch
    test_project.wait_assert_api_branches(
        lambda branches: set(branches) == {top1_gl_branch}
    )

    repo.hg('topic', 'other')
    repo_path.join('foo').write('other')
    repo.hg('commit', '-Am', "Commit 0")
    out, err = repo.hg_with_stderr('push', url)
    top2_gl_branch = 'topic/default/other'
    # The default branch should not have changed, as the first topic
    # still exists.
    assert test_project.api_default_branch() == top1_gl_branch
    test_project.wait_assert_api_branches(
        lambda branches: set(branches) == {top1_gl_branch, top2_gl_branch}
    )

    repo.hg('topic', '-r', '.', 'dev')
    repo.hg('push', url, '-f')
    # Used to break here: the value in file was `top2_gl_branch`, the returned
    # value in API became the ultimate fallback: 'branch/default', which of
    # course does not point to anything yet.
    # At this point the project home page was displaying a 500 error
    assert test_project.api_default_branch() == top1_gl_branch
    test_project.wait_assert_api_branches(
        lambda branches: set(branches) == {top1_gl_branch}
    )

    # now making the topic set as default branch entirely disappear
    repo.hg('topic', '-r', 'stack()', 'yet-another')
    top3_gl_branch = 'topic/default/yet-another'
    repo.hg('push', url, '-f')
    assert test_project.api_default_branch() == top3_gl_branch

    # publishing only the first, to make slightly different from
    # test_only_topic_rename_simple()
    repo.hg('push', '--pub', '-r', 's1', url, expected_return_code=1)
    assert test_project.api_default_branch() == 'branch/default'
    test_project.wait_assert_api_branches(
        lambda branches: set(branches) == {'branch/default',
                                           top3_gl_branch}
    )


def test_topic_branch_change(test_project, tmpdir):
    repo_path = tmpdir.join('repo1')
    url = test_project.owner_basic_auth_url

    repo = LocalRepo.init(repo_path)
    repo_path.join('foo').write('foo0')
    repo.hg('commit', '-Am', "Commit 0")
    repo.hg('branch', 'other')
    repo_path.join('foo').write('foo1')
    repo.hg('commit', '-Am', "Commit 1")
    # avoid topic being default GitLab branch by pushing named branches first
    repo.hg('push', '--publish', url)

    repo.hg('topic', 'zetop')
    repo_path.join('foo').write('foo2')
    repo.hg('commit', '-Am', "Commit 2")
    repo.hg('push', url)

    assert test_project.api_branch_titles() == {
        'branch/default': 'Commit 0',
        'branch/other': 'Commit 1',
        'topic/other/zetop': 'Commit 2',
    }

    repo.hg('branch', '-f', 'default')
    repo.hg('amend')
    repo.hg('push', url)

    # the GitLab branch for the old branch/topic combination has been pruned
    test_project.wait_assert_api_branch_titles({
        'branch/default': 'Commit 0',
        'branch/other': 'Commit 1',
        'topic/default/zetop': 'Commit 2',
    })


def test_topic_publish(test_project, tmpdir):
    repo_path = tmpdir.join('repo1')
    url = test_project.owner_basic_auth_url

    repo = LocalRepo.init(repo_path)
    repo_path.join('foo').write('foo0')
    repo.hg('commit', '-Am', "Commit 0")
    # avoid topic being default GitLab branch by pushing named branches first
    repo.hg('push', '--publish', url)

    repo.hg('topic', 'zetop')
    repo_path.join('foo').write('foo1')
    repo.hg('commit', '-Am', "Commit 1")
    repo.hg('push', url)

    assert test_project.api_branch_titles() == {
        'branch/default': 'Commit 0',
        'topic/default/zetop': 'Commit 1',
    }

    repo.hg('push', '--publish', url, expected_return_code=1)

    # the GitLab branch for the topic has been pruned
    test_project.wait_assert_api_branch_titles({'branch/default': 'Commit 1'})


def test_topic_new_mr_prompt_non_default_target(test_project, tmpdir):
    repo_path = tmpdir.join('repo1')
    url = test_project.owner_basic_auth_url

    repo = LocalRepo.init(repo_path)
    repo_path.join('foo').write('foo0')
    repo.hg('commit', '-Am', "Commit 0")
    repo.hg('branch', 'other')
    repo_path.join('foo').write('foo1')
    repo.hg('commit', '-Am', "Commit 1")
    # avoid topic being default GitLab branch by pushing named branches first
    repo.hg('push', '--publish', url)

    repo.hg('topic', 'zetop')
    repo_path.join('foo').write('foo2')
    repo.hg('commit', '-Am', "Commit 2")
    out = repo.hg('push', url)

    # checking consistency
    assert test_project.api_branch_titles() == {
        'branch/default': 'Commit 0',
        'branch/other': 'Commit 1',
        'topic/other/zetop': 'Commit 2',
    }

    for line in out.splitlines():
        if '/merge_requests/new' in line:
            assert parse_qs(line.split('?')[1]) == {
                'merge_request[source_branch]': ['topic/other/zetop'],
                'merge_request[target_branch]': ['branch/other']}
            break
    else:
        raise AssertionError(
            "No Merge Request creation prompt seen in push output")


def test_topic_new_mr_prompt_unknown_target(test_project, tmpdir):
    """The topic relates to a branch that has no non-topical changeset yet."""
    repo_path = tmpdir.join('repo1')
    url = test_project.owner_basic_auth_url

    repo = LocalRepo.init(repo_path)
    repo_path.join('foo').write('foo0')
    repo.hg('commit', '-Am', "Commit 0")
    repo.hg('branch', 'other')
    # avoid topic being default GitLab branch by pushing named branches first
    repo.hg('push', '--publish', url)

    repo.hg('topic', 'zetop')
    repo_path.join('foo').write('footop')
    repo.hg('commit', '-Am', "In topic")
    out = repo.hg('push', url)

    # checking consistency
    assert test_project.api_branch_titles() == {
        'branch/default': 'Commit 0',
        'topic/other/zetop': 'In topic',
    }
    assert not any('/merge_requests/new' in line for line in out.splitlines())


def test_stacked_topic_amend_first(test_project, tmpdir):
    """In this case, we have two topics, and we amend the first
    """
    repo = LocalRepo.init(tmpdir.join('repo'),
                          default_url=test_project.owner_basic_auth_url)
    repo.path.join('kitten').write("A lion is stronger than a kitten\n")
    repo.hg('commit', '-Am', "Initial sentence")
    repo.hg('phase', '-p', '.')
    repo.hg('topic', 'antelope')
    repo.path.join('antelope').write("A lion is stronger than an antelope\n")
    repo.hg('commit', '-Am', "Même une antilope !",
            '--user', 'Raphaël <raphael@heptapod.test>')
    repo.hg('topic', 'food')
    repo.path.join('food').write("A horse eats grass\n")
    repo.hg('commit', '-Am', "food: horse eats grass")
    print("Graph at first push (before amend of base topic)")
    print(repo.graphlog())
    repo.hg('push', '-r', '.')

    repo.hg('up', 'antelope')
    repo.path.join('independent').write("Antelopes are mammals\n")
    repo.hg('amend', '-Am', "All about antelopes")
    # no need to force push if the client is also on hg-evolve 9.3.1
    print("Graph at second push (after amend of base topic)")
    print(repo.graphlog())
    repo.hg('push', '-r', '.')

    assert test_project.api_branch_titles() == {
        'branch/default': "Initial sentence",
        'topic/default/antelope': "All about antelopes",
        'topic/default/food': "food: horse eats grass",
    }


def test_default_branch_not_topic_push_twice(test_project, tmpdir):
    repo = LocalRepo.init(tmpdir.join('repo'),
                          default_url=test_project.owner_basic_auth_url)
    repo.hg('topic', 'initial')
    repo.path.join('kitten').write("A lion is stronger than a kitten\n")
    repo.hg('commit', '-Am', "Initial sentence")
    repo.hg('push')
    # GitLab wouldn't like a repo that's not empty yet doesn't have
    # a default branch
    assert test_project.api_default_branch() == 'topic/default/initial'
    repo.hg('push', '--publish', expected_return_code=1)
    assert test_project.api_default_branch() == 'branch/default'
    assert 'topic/default/initial' not in test_project.api_protected_branches()

    # subsequent pushes just work
    repo.hg('topic', 'antelope')
    repo.path.join("antelope").write("What's so interesting about antelopes?")
    repo.hg('commit', '-Am', 'antelopes')
    repo.hg('push')

    # for good measure
    assert test_project.api_default_branch() == 'branch/default'
    # the old default topic branch got finally pruned
    assert test_project.api_branch_titles() == {
        'branch/default': "Initial sentence",
        'topic/default/antelope': 'antelopes',
    }


def test_default_branch_not_topic_push_once(test_project, tmpdir):
    """A bunch of topics and a named branch in one single push."""
    repo = LocalRepo.init(tmpdir.join('repo'),
                          default_url=test_project.owner_basic_auth_url)
    repo.hg('branch', 'actual-default')
    repo.path.join('kitten').write("A lion is stronger than a kitten\n")
    repo.hg('commit', '-Am', "Initial sentence")
    repo.hg('phase', '-p', '.')
    repo.hg('branch', 'default')
    for i in range(10):
        # not really necessary but it's nicer than stacking the topics
        repo.hg('up', '0')
        repo.hg('topic', 'side%d' % i)
        repo.path.join('foo').write("foo%d" % i)
        repo.hg('commit', '-Am', "foo%d" % i)

    repo.hg('push')
    assert test_project.api_default_branch() == 'branch/actual-default'
