# -*- coding: utf-8 -*-
import json
import pytest

from selenium.webdriver.common.by import By

from heptapod_tests.access_levels import ProjectAccess
from heptapod_tests.branch import gitlab_branch
from heptapod_tests import hg
from heptapod_tests.merge_request import MergeRequest
from heptapod_tests.project import (
    extract_gitlab_branch_titles,
)
from heptapod_tests.selenium import (
    wait_assert_in_page_source,
    wait_could_click,
    wait_could_click_button,
    window_size,
)

from . import suitable

parametrize = pytest.mark.parametrize


def prepare_topic(repo, branch=None, needing_rebase=True,
                  push_opts=None,
                  ssh_cmd=None, with_ci=False, with_mr_pipelines=False):
    """Prepare a topic to submit merge request.

    Graph after preparation of topic if needing_rebase is True:

    @  2:2cbbb47a340b Même une antilope ! (topic antelope)
    |
    | o  1:d89d3399daef Even a horse!
    |/
    o  0:db4c7a5440ab Initial sentence

    If needing_rebase is False:

    @  1:2cbbb47a340b Même une antilope ! (topic antelope)
    |
    o  0:db4c7a5440ab Initial sentence

    :param branch: if specified, the topic will be set on the given branch.
    :param dict push_opts: translates into several --pushvars statements
    """
    topic_name = 'antelope'
    repo.path.join('kitten').write("A lion is stronger than a kitten\n")
    if with_ci:
        # let's not depend on auto-devops (JSON is a subset of YaML)
        ci_config = dict(job=dict(script=["grep lion antelope"]))
        if with_mr_pipelines:
            ci_config['job']['rules'] = [
                {'if': '$CI_PIPELINE_SOURCE == "merge_request_event"'},
                {'if': '$CI_PIPELINE_SOURCE == "push"'},
            ]
        repo.path.join('.gitlab-ci.yml').write(json.dumps(ci_config))
    repo.hg('commit', '-Am', "Initial sentence")
    if needing_rebase:
        repo.path.join('horse').write("A lion is stronger than a horse\n")
        repo.hg('commit', '-Am', "Even a horse!")
    push_cmd = ['push']
    if ssh_cmd is not None:
        push_cmd.extend(('--ssh', ssh_cmd))
    repo.hg(*push_cmd)
    repo.hg('up', '0')

    if branch is not None:
        repo.hg('branch', branch)
    else:
        branch = 'default'

    repo.hg('topic', topic_name)
    repo.path.join('antelope').write("A lion is stronger than an antelope\n")

    repo.hg('commit', '-Am', "Même une antilope !",
            '--user', 'Raphaël <raphael@heptapod.test>')
    if push_opts:
        push_cmd.extend(hg.cli_pushvars(push_opts))
    out = repo.hg(*push_cmd)

    auto_create_mr = push_opts and 'merge_request.create' in push_opts
    # there is no natural target if branch is not default.
    if branch == 'default' and not auto_create_mr:
        assert f'create a merge request for topic/{branch}/{topic_name}' in out
    print("Graph after preparation of topic:")
    print(repo.graphlog())
    return topic_name


def prepare_stacked_linear_topics(repo):
    topic1 = prepare_topic(repo, needing_rebase=False)
    topic2 = 'food'

    repo.hg('up', topic1)  # the fact that we are already on it is coincidental
    repo.hg('topic', topic2)
    repo.path.join('food').write("A horse eats grass\n")
    repo.hg('commit', '-Am', "food: horse eats grass")
    print("Graph at initial push of second topic")
    print(repo.graphlog())
    repo.hg('push', '-r', '.')
    return topic1, topic2


def prepare_named_branch(repo, needing_rebase=True, branch_name=None):
    """Prepare a named branch to submit merge request.

    Here's the produced graph if `needing_rebase` is True::

      @  2:b2c6274c4f74 Le lion est prédateur du gnou ! (branch: gnu)
      |
      | o  1:19a46ba6d021 Even a horse!
      |/
      o  0:1fd69a3d35ba Initial sentence

    """
    if branch_name is None:
        branch_name = 'gnu'
    repo.path.join('kitten').write("A lion is stronger than a kitten\n")
    repo.hg('commit', '-Am', "Initial sentence")
    if needing_rebase:
        repo.path.join('horse').write("A lion is stronger than a horse\n")
        repo.hg('commit', '-Am', "Even a horse!")
    repo.hg('push')
    repo.hg('up', '0')
    repo.hg('branch', branch_name)
    repo.path.join('gnu').write("A lion eats lots of gnu!\n")
    repo.hg('commit', '-Am', "Le lion est prédateur du gnou !",
            '--user', 'Raphaël <raphael@heptapod.test>')
    repo.hg('push', '--new-branch')
    print("Graph after preparation of named branch:")
    print(repo.graphlog())
    return branch_name


def api_create_mr(project, topic=None, hg_branch='default',
                  target_hg_branch='default'):
    """A shortcut for the most common case.

    Other cases can be simply handled by using `MergeRequest.api_create()`
    """
    return MergeRequest.api_create(
        project,
        source_branch=gitlab_branch(branch=hg_branch, topic=topic),
        target_branch=gitlab_branch(branch=hg_branch))


def rebase(repo, topic):
    repo.hg('rebase', '-s', 'first(topic(%s))' % topic, '-d', 'default')
    print("Full graph after rebase of topic %s" % topic)
    print(repo.graphlog(hidden=True))


def rebase_publish_push(repo, topic):
    """Rebase the topic created with `prepare_topic()`, publish and push.

    Return full Node ID of the topic head after rebase and before publication
    """
    rebase(repo, topic)
    sha = repo.node(topic)
    repo.hg('push', '--publish')
    print("Graph after push/publish:")
    print(repo.graphlog())
    return sha


def assert_user_cannot_merge(user_name, project, mr_id):
    user = project.heptapod.get_user(user_name)
    mr = MergeRequest(project, mr_id)
    mr.assert_user_cannot_merge(user)


def test_mergerequest_rebase_publish(test_project, tmpdir):
    """
    When a topic is rebased and pushed with the --publish flag,
    the published topic was not correctly handled by Heptapod,
    and going to the corresponding merge request resulted in a 500 error.
    This test makes sure that this case is handled correctly.
    """
    repo = hg.LocalRepo.init(tmpdir.join('repo'),
                             default_url=test_project.owner_basic_auth_url)
    topic = prepare_topic(repo)
    mr = api_create_mr(test_project, topic=topic)
    topic_sha = rebase_publish_push(repo, topic)

    # merge has been detected and displays the right commit
    mr.wait_assert_merged(expected_source_branch_category='topic')
    mr.assert_commit_link("Même une antilope !", topic_sha)


def test_mergerequest_auto_create(test_project, tmpdir):
    repo = hg.LocalRepo.init(tmpdir.join('repo'),
                             default_url=test_project.owner_basic_auth_url)
    topic = prepare_topic(repo, push_opts={
        'merge_request.create': True,
        'merge_request.title': "Created by pushvar",
        'merge_request.description': "Automatic",
    })
    # ideally, it should be parsable from the push message, but
    # we're pretty sure of the iid anyway
    MergeRequest(test_project, 1).wait_assert(
        lambda mr: (mr is not None
                    and mr['state'] == 'opened'
                    and mr['source_branch'] == gitlab_branch(topic=topic)
                    and mr['target_branch'] == gitlab_branch()
                    and mr['merge_status'] == 'can_be_merged'
                    ))


def test_mergerequest_topic_different_branch_publish(test_project, tmpdir):
    """Case where the topic refers to another branch than the MR target.
    """
    repo = hg.LocalRepo.init(tmpdir.join('repo'),
                             default_url=test_project.owner_basic_auth_url)
    topic = prepare_topic(repo, branch='other')
    topic_sha = repo.node(topic)

    mr = MergeRequest.api_create(test_project,
                                 source_branch=gitlab_branch(branch='other',
                                                             topic=topic),
                                 target_branch=gitlab_branch(branch='default'),
                                 )

    repo.hg('up', 'default')
    repo.hg('merge', topic)
    repo.hg('commit',
            '-m', "Merged topic on branch other into branch default",
            '--user', 'Raphaël <raphael@heptapod.test>')

    repo.hg('push', '--publish')
    print("Graph after push/publish:")
    print(repo.graphlog())
    # and merge has been detected
    mr.wait_assert_merged(expected_source_branch_category='topic')

    assert test_project.api_branch_titles() == {
        'branch/default': "Merged topic on branch other into branch default",
        'branch/other': "Même une antilope !",
    }

    mr.assert_commit_link("Même une antilope !", topic_sha)


def test_mergerequest_stacked_rebase_publish(test_project, tmpdir):
    """In this case, we have two topics, and we only rebase the second.

    This is the original scenario of heptapod#43
    """
    repo = hg.LocalRepo.init(tmpdir.join('repo'),
                             default_url=test_project.owner_basic_auth_url)
    topic1, topic2 = prepare_stacked_linear_topics(repo)
    mr = api_create_mr(test_project, topic=topic2)

    repo.hg('rebase', '-r', '.', '-d', 'default')
    print("Graph after rebase")
    print(repo.graphlog())

    # no need to force
    repo.hg('push', '-r', topic2, '--publish')
    # and merge has been detected
    mr.wait_assert_merged(expected_source_branch_category='topic')


def test_mergerequest_api_stacked_publish_first(test_project, tmpdir):
    """In this case, we have two MRs and we publish the second.

    This is heptapod#215
    """
    repo = hg.LocalRepo.init(tmpdir.join('repo'),
                             default_url=test_project.owner_basic_auth_url)

    topic1, topic2 = prepare_stacked_linear_topics(repo)
    topic1_head_title = "Même une antilope !"

    mr1 = api_create_mr(test_project, topic=topic1)
    mr2 = api_create_mr(test_project, topic=topic2)

    mr1.api_accept()

    # update of mr2 is asynchronous, so we'll have to wait_assert() it

    def is_updated(mr_info):
        shas = mr_info['diff_refs']
        return all(
            test_project.api_commit(shas[sha])['title'] == topic1_head_title
            for sha in ('start_sha', 'base_sha')
        )

    mr2.wait_assert(is_updated,
                    retry_wait_factor=0.1,
                    msg="Expected update of second MR didn't happen "
                    "after {timeout} seconds")
    commit_links = mr2.webdriver_get_commit_links()
    assert len(commit_links) == 1
    assert 'food: horse eats grass' in commit_links[0].text


def test_mergerequest_api_stacked_publish_second(test_project, tmpdir):
    """In this case, we have two MRs and we publish the second.

    This is heptapod#261
    """
    repo = hg.LocalRepo.init(tmpdir.join('repo'),
                             default_url=test_project.owner_basic_auth_url)

    topic1, topic2 = prepare_stacked_linear_topics(repo)
    mr1 = api_create_mr(test_project, topic=topic1)
    mr2 = api_create_mr(test_project, topic=topic2)

    mr2.api_accept()
    mr1.wait_assert_merged()


def test_mergerequest_stacked_amend_publish_first(test_project, tmpdir):
    """In this case, we have two topics, and we only rebase the first.
    """
    repo = hg.LocalRepo.init(tmpdir.join('repo'),
                             default_url=test_project.owner_basic_auth_url)
    topic = prepare_topic(repo, needing_rebase=False)
    mr = api_create_mr(test_project, topic=topic)

    repo.hg('up', topic)  # the fact that we are already on it is coincidental
    repo.hg('topic', 'food')
    repo.path.join('food').write("A horse eats grass\n")
    repo.hg('commit', '-Am', "food: horse eats grass")
    print("Graph at first push (before amend of base topic)")
    print(repo.graphlog())
    repo.hg('push', '-r', '.')

    repo.hg('up', topic)
    repo.path.join('independent').write("Antelopes are mammals\n")
    repo.hg('amend', '-A')
    # no need to force push if the client is also on hg-evolve 9.3.1
    print("Graph at second push (after amend of base topic)")
    print(repo.graphlog())
    repo.hg('push', '-r', '.', '--publish')
    amended_sha = repo.node('.')

    # and merge has been detected
    # in the case of native Mercurial, the topic is still visible in the
    # branchmap because it has orphan descendent. We could add the same kind
    # of filtering in HGitaly than multiple heads detection and
    # py_heptapod's mirror perform, but that is slow for a read operation
    # that happens all the time (listing branches). Better to say in the
    # short term that we don't care.
    mr.wait_assert_merged(
        check_source_branch_removal=not test_project.hg_native)

    mr.assert_commit_link("Même une antilope !", amended_sha)


def test_mergerequest_webdriver_create(test_project, tmpdir):
    """Test that the creation web page works and proceed.
    """
    repo = hg.LocalRepo.init(tmpdir.join('repo'),
                             default_url=test_project.owner_basic_auth_url)
    topic = prepare_topic(repo)
    source_branch = gitlab_branch(topic=topic)
    mr = MergeRequest.webdriver_create(
        source_project=test_project,
        source_branch=source_branch,
    )
    rebase_publish_push(repo, topic)

    # and merge has been detected
    mr.wait_assert_merged(expected_source_branch=source_branch)


def test_mergerequest_add_rebase_publish(test_project, tmpdir):
    """same as rebase_publish, with an additional topic changeset in the push.

    The motivation is that is could be more complicated to related the
    published topic head, because it's just not the same changeset, and
    it's not linked to the previous one by obsolescence markers either.
    """
    repo = hg.LocalRepo.init(tmpdir.join('repo'),
                             default_url=test_project.owner_basic_auth_url)
    topic = prepare_topic(repo)
    mr = api_create_mr(test_project, topic=topic)

    repo.path.join('elephant').write("but an elephant trumps the lion\n")
    additional_msg = "Not an elephant!"
    repo.hg('commit', '-Am', additional_msg)
    assert repo.hg('log', '-T', "{topic}", '-r', '.') == topic

    rebase_publish_push(repo, topic)
    rebased_sha = repo.node('.')

    mr.wait_assert_merged()
    mr.assert_commit_link(additional_msg, rebased_sha)


@suitable.prod_server
def test_mergerequest_rebase_push_then_publish(test_project, tmpdir):
    """A simpler scenario for Heptapod: pushing the rebase, then publishing.

    Related to issue 47, but does not pass either at the time of this writing
    The reason being probably that the disappearance of the topic due to
    publication prevents the Rails application to perform its detection.
    """
    repo = hg.LocalRepo.init(tmpdir.join('repo'),
                             default_url=test_project.owner_basic_auth_url)
    topic = prepare_topic(repo)
    mr = api_create_mr(test_project, topic=topic)

    rebase(repo, topic)
    rebased_sha = repo.node(topic)
    repo.hg('push')
    repo.hg('phase', '--public', '-r', topic)
    print("Full graph after publishing:")
    print(repo.graphlog(hidden=True))
    # hg push gives return code 1 because there aren't any changesets to push
    repo.hg('push', check_return_code=False)

    # Detection worked
    mr.wait_assert_merged(expected_source_branch_category='topic')

    # Commit list is correct
    mr.assert_commit_link("Même une antilope !", rebased_sha)


def test_mergerequest_api_fast_forward_result(test_project_with_runner,
                                              tmpdir):
    """Accepting the MR via API.

    In this test, Heptapod does it without a merge (Git equivalent would be a
    simple fast-forward).

    Using the API is quite close to clicking that big "merge" button, but it
    has some differences, seen with a lingering bug in hg-git:

    - through the API, this test would give first the correct 200 response
      but the state of the MR was still 'opened' and the commits not published.
    - though the regular UI, we had an error message.

    and actually, we go through hg-git etc anyway: GitLab after all just
    calls the hg executable
    """
    test_project, runner = test_project_with_runner
    repo = hg.LocalRepo.init(tmpdir.join('repo'),
                             default_url=test_project.owner_basic_auth_url)
    topic = prepare_topic(repo, needing_rebase=False, with_ci=True)
    topic_sha = repo.node(topic)
    mr = api_create_mr(test_project, topic=topic)

    jobs = runner.wait_assert_jobs(2)

    assert set(job['git_info']['ref']
               for job in jobs) == {'branch/default',
                                    'topic/default/antelope'}

    # heptapod#332: a mere Developer does not have the right to merge
    # this is the simplest case, because the GitLab default branch is protected
    basic_user = test_project.heptapod.get_user('test_basic')
    test_project.grant_member_access(user=basic_user,
                                     level=ProjectAccess.DEVELOPER)
    mr.assert_user_cannot_merge(basic_user)

    # now merging as the owner
    mr.api_accept()

    repo.hg('pull')
    log = repo.hg('log', '-T', '{rev}:{phase}\n')
    # unchanged revnos proves that Heptapod didn't do anything funky
    assert log.splitlines() == ['1:public', '0:public']

    # there's a CI job for the target
    job = runner.wait_assert_one_job()
    vcs_info = job['git_info']
    assert vcs_info['ref'] == 'branch/default'

    # Commit list is correct
    mr.assert_commit_link("Même une antilope !", topic_sha)


@parametrize('fast_forward', ('as-merge', 'as-ff'))
@parametrize('allowed_to_merge', ('publisher-allowed', 'maintainer-allowed'))
def test_mergerequest_protected_branch(test_project, tmpdir,
                                       allowed_to_merge, fast_forward):
    """The point of this test is to validate protected branch access level.

    We're using the fast forwardable case because… it's supposed to be fast.
    """
    repo = hg.LocalRepo.init(tmpdir.join('repo'),
                             default_url=test_project.owner_basic_auth_url)
    if fast_forward == 'as-ff':
        test_project.api_update_merge_request_settings(merge_method='ff')
    topic = prepare_topic(repo, needing_rebase=False)
    mr = api_create_mr(test_project, topic=topic)

    # Scenario: user will start with not_allowed_level, then will be granted
    # allowed_level.
    if allowed_to_merge == 'publisher-allowed':
        allowed_level = ProjectAccess.HG_PUBLISHER
        not_allowed_level = ProjectAccess.DEVELOPER
    elif allowed_to_merge == 'maintainer-allowed':
        allowed_level = ProjectAccess.MAINTAINER
        not_allowed_level = ProjectAccess.HG_PUBLISHER
    test_project.api_protect_branch('branch/default',
                                    merge_access_level=allowed_level)

    user_name = 'test_basic'
    user = test_project.heptapod.get_user(user_name)

    # merge is refused if not enough rights
    test_project.grant_member_access(user=user, level=not_allowed_level)
    mr.assert_user_cannot_merge(user)

    repo.hg('pull')
    Extract, extracts = repo.changeset_extracts(('desc', 'topic', 'phase'))
    assert extracts[0] == Extract(desc='Même une antilope !',
                                  topic='antelope',
                                  phase='draft')

    # merge is accepted with enough rights
    test_project.grant_member_access(user=user, level=allowed_level)
    mr.api_accept(user=user)

    repo.hg('pull')
    Extract, extracts = repo.changeset_extracts(('desc', 'phase'))
    assert extracts[0] == Extract(desc='Même une antilope !', phase='public')


def test_mergerequest_api_fast_forward_required(test_project, tmpdir):
    """Accepting a MR configured for fast-forward only via API.
    """
    repo = hg.LocalRepo.init(tmpdir.join('repo'),
                             default_url=test_project.owner_basic_auth_url)
    test_project.api_update_merge_request_settings(merge_method='ff')

    default_gl_branch = gitlab_branch(branch='default')
    topic = prepare_topic(repo, needing_rebase=False)
    topic_sha = repo.node(topic)
    mr = api_create_mr(test_project, topic=topic)

    mr.api_accept()
    test_project.wait_assert_api_branches(
        lambda branches: extract_gitlab_branch_titles(branches) == {
            default_gl_branch: 'Même une antilope !'})
    repo.hg('pull')
    log = repo.hg('log', '-T', '{rev}:{phase}\n')
    # unchanged revnos proves that Heptapod didn't do anything funky
    assert log.splitlines() == ['1:public', '0:public']

    # Commit list is correct
    mr.assert_commit_link("Même une antilope !", topic_sha)

    # now let's make a new changeset that would be a fast-forward for
    # Git at first sight (DAG is linear) but wouldn't be for Mercurial
    # because it has a different named branch
    repo.hg('topic', 'whale')
    repo.hg('branch', 'sea')
    repo.path.join('whale').write("A lion would be puzzled to see a whale")
    repo.hg('commit', '-Am', "Whale")
    repo.hg('push')
    whale_gl_branch = gitlab_branch(branch='sea', topic='whale')
    test_project.wait_assert_api_branch_titles({
        default_gl_branch: 'Même une antilope !',
        whale_gl_branch: 'Whale',
    })

    mr = MergeRequest.api_create(test_project,
                                 source_branch=whale_gl_branch,
                                 target_branch=default_gl_branch)
    mr.api_accept(check_merged=False)

    # Ideally we should have had an error, but that's not the case as of
    # this writing. Meanwhile, nothing has changed

    test_project.wait_assert_api_branch_titles({
        default_gl_branch: 'Même une antilope !',
        whale_gl_branch: 'Whale',
    })
    repo.hg('pull')
    log = repo.hg('log', '-T', '{rev}:{topic}:{phase}\n')
    # unchanged revnos proves that Heptapod didn't do anything funky
    assert log.splitlines() == ['2:whale:draft', '1::public', '0::public']


def test_mergerequest_api_semi_linear(test_project, tmpdir):
    """Accepting a MR configured for semi-linear workflow.
    """
    repo = hg.LocalRepo.init(tmpdir.join('repo'),
                             default_url=test_project.owner_basic_auth_url)
    test_project.api_update_merge_request_settings(
        merge_method='rebase_merge',
    )

    default_gl_branch = gitlab_branch(branch='default')
    topic = prepare_topic(repo, needing_rebase=False)
    mr = api_create_mr(test_project, topic=topic)

    mr.api_accept()

    merge_desc = "Merge branch '%s' into '%s'" % (gitlab_branch(topic=topic),
                                                  default_gl_branch)
    test_project.wait_assert_api_branches(
        lambda branches: extract_gitlab_branch_titles(branches) == {
            default_gl_branch: merge_desc
        })

    repo.hg('pull')
    log = repo.hg('log', '-T', '{rev}:{phase}\n')
    # unchanged revnos proves that Heptapod didn't do anything funky
    assert log.splitlines() == ['2:public', '1:public', '0:public']

    # now let's make a new changeset that would be a fast-forward for
    # Git at first sight (DAG is linear) but wouldn't be for Mercurial
    # because it has a different named branch
    repo.hg('topic', 'whale')
    repo.hg('branch', 'sea')
    repo.path.join('whale').write("A lion would be puzzled to see a whale")
    repo.hg('commit', '-Am', "Whale")
    repo.hg('push')
    whale_gl_branch = gitlab_branch(branch='sea', topic='whale')
    test_project.wait_assert_api_branch_titles({
        default_gl_branch: merge_desc,
        whale_gl_branch: 'Whale',
    })

    mr = MergeRequest.api_create(test_project,
                                 source_branch=whale_gl_branch,
                                 target_branch=default_gl_branch)
    mr.api_accept(check_merged=False)

    # Ideally we should have had an error, but that's not the case as of
    # this writing. In the meanwhile, nothing has changed

    assert test_project.api_branch_titles() == {
        default_gl_branch: merge_desc,
        whale_gl_branch: 'Whale',
    }
    repo.hg('pull')
    log = repo.hg('log', '-T', '{rev}:{topic}:{phase}\n')
    # unchanged revnos proves that Heptapod didn't do anything funky
    assert log.splitlines() == [
        '3:whale:draft',
        '2::public',
        '1::public',
        '0::public',
    ]


def test_mergerequest_api_fast_forward_refusal_rebase(test_project, tmpdir):
    """Accepting the MR via API with rebase scenario.

    see `test_mergerequest_api()` for relevance of API call for testing.

    Non-ASCII side of this test:
    with the MR created through the webdriver, it gets title and
    description, which end up in the merge commit message.
    """
    test_project.api_update_merge_request_settings(merge_method='ff')
    default_url = test_project.owner_basic_auth_url
    repo = hg.LocalRepo.init(tmpdir.join('repo'),
                             default_url=default_url)
    topic = prepare_topic(repo)
    mr = api_create_mr(test_project, topic=topic)

    # TODO here it would be nice to wait for mergeability analysis to
    # conclude with a `mr.wait_assert()` but strangely trying it gave
    # `merge_status` value of `can_be_merged`. It could be a starting point
    # before a worker actually changes it. In any case, not something reliable
    # to test.

    resp = mr.api_accept(check_merged=False)
    # GitLab 15.2 changes the status code from 406 to 422,
    # see the comment thread at https://gitlab.com/gitlab-org/gitlab
    #                             /-/merge_requests/82465/#note_879486669
    # (actually changing default value of corresponding feature flag to true)
    assert resp.status_code in (406, 422)
    # as of this writing, the resulting message is not worth doing
    # meaningful assertions: {'message': 'Branch cannot be merged'}
    # (and the 406 status code is the same as with conflicts)

    mr.api_rebase()
    mr.api_accept(wait_mergeability=True)
    test_project.wait_assert_api_branch_titles(
        {gitlab_branch(): "Même une antilope !"})

    repo.hg('pull', '-u')  # update to stop being on an obsolete changeset
    print("Graph after API rebase and fast-forward accept:")
    print(repo.graphlog(hidden=True))

    log = repo.hg('log', '-T', '{desc|firstline}:{phase}\n')
    assert log.splitlines() == [
        "Même une antilope !:public",
        "Even a horse!:public",
        "Initial sentence:public",
    ]

    # Commit list is correct
    mr.assert_commit_link("Même une antilope !", repo.node('default'))


def test_mergerequest_developer_cannot_merge(test_project, tmpdir):
    repo = hg.LocalRepo.init(tmpdir.join('repo'),
                             default_url=test_project.owner_basic_auth_url)
    topic = prepare_topic(repo, needing_rebase=False)
    repo.hg('update', 'default')
    repo.hg('branch', 'other')
    repo.path.join('foo').write("foo")
    repo.hg('commit', '-Am', "Starting MR target branch")
    repo.hg('push', '--publish', '-r', '.', '--new-branch')
    mr = MergeRequest.api_create(test_project,
                                 source_branch=gitlab_branch(topic=topic),
                                 target_branch=gitlab_branch(branch='other'))
    basic_user = test_project.heptapod.get_user('test_basic')
    test_project.grant_member_access(user=basic_user,
                                     level=ProjectAccess.DEVELOPER)
    mr.assert_user_cannot_merge(basic_user)

    driver = basic_user.webdriver

    driver.get(mr.url)
    wait_assert_in_page_source(
        driver,
        'Ready to merge by members who can write to the target branch'
    )


@parametrize('fast_forward', ['no', 'required'])
def test_mergerequest_api_target_topic(test_project, tmpdir, fast_forward):
    """Accepting the MR via API with rebase scenario.

    see `test_mergerequest_api()` for relevance of API call for testing.

    Non-ASCII side of this test:
    with the MR created through the webdriver, it gets title and
    description, which end up in the merge commit message.
    """
    if fast_forward == 'required':
        test_project.api_update_merge_request_settings(merge_method='ff')
    default_url = test_project.owner_basic_auth_url
    repo_path = tmpdir.join('repo')
    repo = hg.LocalRepo.init(repo_path, default_url=default_url)
    target_topic = prepare_topic(repo)
    source_topic = 'zetop'

    branching_point = target_topic if fast_forward == 'required' else 'default'
    repo.hg('up', branching_point)
    repo.hg('topic', source_topic)
    repo_path.join('foo').write("bar")
    repo.hg('commit', '-Am', "something else")
    repo.hg('push')

    mr = MergeRequest.api_create(
        test_project,
        source_branch=gitlab_branch(topic=source_topic),
        target_branch=gitlab_branch(topic=target_topic),
        title="targeting a topic")

    mr.wait_assert(
        lambda info: info.get('merge_status') == 'cannot_be_merged',
        msg="Mergeability wrong or still unknown after {timeout} seconds")

    resp = mr.api_accept(check_merged=False, wait_mergeability=False)
    assert resp.status_code >= 400 and resp.status_code < 500


@parametrize('push_proto', ['ssh', 'http'])
def test_mergerequest_api_explicit_merge_message(test_project_with_runner,
                                                 tmpdir,
                                                 push_proto):
    """Accepting the MR via API with rebase scenario.

    see `test_mergerequest_api()` for relevance of API call for testing.

    Non-ASCII side of this test:
    with the MR created through the webdriver, it gets title and
    description, which end up in the merge commit message.
    """
    test_project, runner = test_project_with_runner
    if push_proto == 'http':
        ssh_cmd, default_url = None, test_project.owner_basic_auth_url
    elif push_proto == 'ssh':
        ssh_cmd, default_url = test_project.owner_ssh_params
    repo = hg.LocalRepo.init(tmpdir.join('repo'),
                             default_url=default_url)
    topic = prepare_topic(repo, ssh_cmd=ssh_cmd, with_ci=True)
    topic_sha = repo.node(topic)
    mr = api_create_mr(test_project, topic=topic)

    jobs = runner.wait_assert_jobs(2)
    assert set(job['git_info']['ref']
               for job in jobs) == {'branch/default',
                                    'topic/default/antelope'}

    mr.api_accept()
    repo.hg('pull', test_project.owner_basic_auth_url)
    print("Graph after API merge:")
    print(repo.graphlog(hidden=True))
    log = repo.hg('log', '-T', '{desc|firstline}:{phase}\n')
    assert log.splitlines() == [
        "Merge branch 'topic/default/antelope' into 'branch/default':public",
        "Même une antilope !:public",
        "Even a horse!:public",
        "Initial sentence:public",
    ]

    # there's a CI job for the target
    job = runner.wait_assert_one_job()
    vcs_info = job['git_info']
    assert vcs_info['ref'] == 'branch/default'
    assert vcs_info['hgsha'] == repo.hg('log', '-T', "{node}", '-r', "default")

    mr.assert_commit_link("Même une antilope !", topic_sha)


def test_mergerequest_api_explicit_merge_multiple_heads(test_project, tmpdir):
    """A case with allow multiple heads around.

    This can work only if repo specific HGRC is taken into account during
    server-side merges (see heptapod#324).
    """
    # allowing multiple heads is the focus of the test.
    # we're adding auto_publish=nothing just to take the opportunity
    # to prove that the MR acceptation does not publish other changesets
    # than it should (auto publication is relevant to pushes only in
    # standard Mercurial, but one day Heptapod will base some decisions
    # in its operations based on it.
    test_project.api_hgrc_set(inherit=False,
                              auto_publish="nothing",
                              allow_multiple_heads=True)

    repo_path = tmpdir.join('repo')
    repo = hg.LocalRepo.init(repo_path,
                             default_url=test_project.owner_basic_auth_url)
    topic = prepare_topic(repo)
    # now let's create an unrelated multiple heads situation in another branch
    repo.hg('up', '0')
    repo.hg('branch', 'flora')
    repo.hg('topic', '--clear')
    repo.hg('commit', '-m', "Creating 'flora' branch")
    repo.hg('phase', '-p', '.')

    repo.path.join('flora').write("Why only animals ? ")
    repo.hg('commit', '-Am', "Multiple head 1")

    repo.hg('up', 'min(branch(flora))')
    repo.path.join('plants').write("Let's talk about plants")
    repo.hg('commit', '-Am', "Multiple head 2")
    print("Graph before MR creation")
    print(repo.hg('log', '-G', '-T',
                  "[{branch}] {rev}:{node|short} {desc|firstline}"))
    repo.hg('push', '--new-branch', '-f')

    mr = api_create_mr(test_project, topic=topic)

    mr.api_accept()
    repo.hg('pull', test_project.owner_basic_auth_url)
    print("Graph after API merge:")
    print(repo.graphlog(hidden=True))

    Extract, extracts = repo.changeset_extracts(('phase',
                                                 ('desc', 'desc|firstline'),
                                                 ),
                                                revs='branch(default)')
    assert extracts == (
        Extract(desc="Initial sentence", phase='public'),
        Extract(desc="Even a horse!", phase='public'),
        Extract(desc="Même une antilope !", phase='public'),
        Extract(desc="Merge branch 'topic/default/antelope' "
                "into 'branch/default'",
                phase='public'),
    )

    # changesets from the 'flora' branch are completely untouched, they
    # don't even have new descendents.
    Extract, extracts = repo.changeset_extracts(('desc', 'phase'),
                                                revs='branch(flora)::',
                                                collection=set)
    assert extracts == {
        Extract(desc="Multiple head 2", phase='draft'),
        Extract(desc="Multiple head 1", phase='draft'),
        Extract(desc="Creating 'flora' branch", phase='public'),
    }


@parametrize('fast_forward', ['no', 'de facto', 'required'])
def test_mergerequest_api_squash(test_project, tmpdir, fast_forward):
    """Accepting the MR via API with squash
    """
    linear = fast_forward != 'no'
    if fast_forward == 'required':
        test_project.api_update_merge_request_settings(merge_method='ff')

    repo = hg.LocalRepo.init(tmpdir.join('repo'),
                             default_url=test_project.owner_basic_auth_url)
    topic = prepare_topic(repo, needing_rebase=not linear)
    # let's add another changeset in topic
    repo.path.join('antelope').write("Gnus are antelopes!\n", mode='a')
    repo.hg('commit', '-Am', "Gnus are no exceptions",
            '--user', 'Raphaël <raphael@heptapod.test>')
    repo.hg('push')

    mr = api_create_mr(test_project, topic=topic)

    resp = mr.api_accept(check_merged=False,
                         squash=True,
                         squash_commit_message="Antelopes including gnus")
    assert resp.status_code == 200  # not equivalent to check_merged=True

    # with squash, the change of status operation can be async.
    mr.wait_assert_merged()

    repo.hg('pull', test_project.owner_basic_auth_url)
    # don't stay on obsolete changesets, lest we pollute the log
    repo.hg('up', 'default')
    print("Graph after API merge:")
    print(repo.graphlog(hidden=True))
    Extract, extracts = repo.changeset_extracts(('phase',
                                                 ('desc', 'desc|firstline'),
                                                 ),
                                                collection=list)
    expected = [Extract(desc="Antelopes including gnus", phase='public'),
                Extract(desc="Initial sentence", phase='public')]
    if not linear:
        expected.insert(1, Extract(desc="Even a horse!", phase='public'))
        expected.insert(0,
                        Extract(desc="Merge branch 'topic/default/antelope' "
                                "into 'branch/default'",
                                phase='public'))
    assert extracts == expected


def test_mergerequest_api_conflict(test_project, tmpdir):
    repo = hg.LocalRepo.init(tmpdir.join('repo'),
                             default_url=test_project.owner_basic_auth_url)
    topic = prepare_topic(repo)
    repo.path.join('horse').write("A lion is stronger than a donkey\n")
    repo.hg('commit', '-Am', "Même un âne",
            '--user', 'Raphaël <raphael@heptapod.test>')
    repo.hg('push')

    mr = api_create_mr(test_project, topic=topic)
    mr.wait_assert(lambda info: info.get('merge_status') == 'cannot_be_merged')

    resp = mr.api_accept(check_merged=False, wait_mergeability=False)

    # see doc/api/merge_requests.md
    assert resp.status_code == 422


def test_mergerequest_api_inside_file(test_project, tmpdir):
    """Test a case where a file has been modified in both branches.

    The merge is possible only using a 3-way resolution algorithm, and
    would fail if Heptapod was using the `internal:fail` merge tool.
    """
    repo = hg.LocalRepo.init(tmpdir.join('repo'),
                             default_url=test_project.owner_basic_auth_url)
    repo.path.join("foo").write("line 1\n\n\nLine 2\n")
    repo.hg('ci', '-Am', 'base')
    repo.path.join("foo").write("Line one\n\n\nLine 2\n")
    repo.hg('ci', '-m', 'target')
    repo.hg('push')
    repo.hg('up', '0')
    repo.hg('topic', 'zetop')
    repo.path.join("foo").write("line 1\n\n\nLine two\n")
    repo.hg('ci', '-m', 'source')
    repo.hg('push')

    mr = api_create_mr(test_project, topic='zetop')
    mr.api_accept()
    mr.wait_assert_merged()

    assert test_project.api_branch_titles() == {
        'branch/default': ("Merge branch 'topic/default/zetop' "
                           "into 'branch/default'")
    }
    repo.hg('pull')
    assert repo.hg('phase', '-r', 'default').strip() == '3: public'
    repo.hg('up', 'default')
    assert repo.path.join("foo").read() == "Line one\n\n\nLine two\n"


@parametrize('push_proto', ['ssh', 'http'])
def test_mergerequest_api_explicit_merge_user(public_project, tmpdir,
                                              push_proto):
    """Accepting the MR via API with rebase scenario.

    see `test_mergerequest_api()` for relevance.
    Using public_project for ASCII testing of the user (full) name,
    because it belongs to basic user.
    TODO all projects should belong to basic_user

    In this test, we create the MR through the API, because the wedriver
    creation works for root only at this point, root having a simpler
    succession of pages to go through (TODO as well)
    """
    if push_proto == 'http':
        ssh_cmd, default_url = None, public_project.owner_basic_auth_url
    elif push_proto == 'ssh':
        ssh_cmd, default_url = public_project.owner_ssh_params
    repo = hg.LocalRepo.init(tmpdir.join('repo'),
                             default_url=default_url)
    topic = prepare_topic(repo, ssh_cmd=ssh_cmd)
    mr = api_create_mr(public_project, topic=topic)

    mr.api_accept()
    mr.wait_assert_merged()

    repo.hg('pull', public_project.owner_basic_auth_url)
    print("Graph after API merge:")
    print(repo.graphlog(hidden=True))

    Extract, extracts = repo.changeset_extracts(('phase',
                                                 ('desc', 'desc|firstline'),
                                                 ))
    assert extracts == (
        Extract(desc="Merge branch 'topic/default/antelope' "
                "into 'branch/default'",
                phase='public'),
        Extract(desc="Même une antilope !", phase='public'),
        Extract(desc="Even a horse!", phase='public'),
        Extract(desc="Initial sentence", phase='public'),
    )


@parametrize('linear', ('linear', 'ramified'))
def test_mergerequest_api_named_branch(public_project, tmpdir, linear):
    """Accepting the MR for a named branch via API (no rebase).

    Using public_project for ASCII testing of the user (full) name,
    because it belongs to basic user.
    TODO all projects should belong to basic_user

    In this test, we create the MR through the API, because the wedriver
    creation works for root only at this point, root having a simpler
    succession of pages to go through (TODO as well)
    """
    ramified = linear == 'ramified'
    repo = hg.LocalRepo.init(tmpdir.join('repo'),
                             default_url=public_project.owner_basic_auth_url)
    branch = prepare_named_branch(repo, needing_rebase=ramified)
    head_sha = repo.node(branch)
    mr = MergeRequest.api_create(public_project,
                                 source_branch=gitlab_branch(branch),
                                 target_branch=gitlab_branch('default'))

    mr.api_accept()
    mr.wait_assert_merged(check_source_branch_removal=False)

    repo.hg('pull')
    print("Graph after API merge:")
    print(repo.graphlog(hidden=True))
    log = repo.hg('log', '-T', '{desc|firstline}:{branch}:{phase}\n')
    expected_log_lines = [
        "Merge branch 'branch/gnu' into 'branch/default':default:public",
        "Le lion est prédateur du gnou !:gnu:public",
        "Initial sentence:default:public",
    ]
    if ramified:
        expected_log_lines.insert(-1, "Even a horse!:default:public")

    assert log.splitlines() == expected_log_lines

    # Commit list is correct
    mr.assert_commit_link("Le lion est prédateur", head_sha)


@parametrize('close', ('no-close', 'close-before', 'close-after'))
def test_mergerequest_cli_named_branch(public_project, tmpdir, close):
    """Accepting the MR for a named branch via CLI (no rebase).

    Using public_project for ASCII testing of the user (full) name,
    because it belongs to basic user.
    TODO all projects should belong to basic_user

    In this test, we create the MR through the API, because the wedriver
    creation works for root only at this point, root having a simpler
    succession of pages to go through (TODO as well)
    """
    repo = hg.LocalRepo.init(tmpdir.join('repo'),
                             default_url=public_project.owner_basic_auth_url)
    branch = prepare_named_branch(repo)
    gl_branch = gitlab_branch(branch)
    head_sha = repo.node(branch)
    mr = MergeRequest.api_create(public_project,
                                 source_branch=gl_branch,
                                 target_branch=gitlab_branch('default'))

    if close == 'close-before':
        repo.hg('commit', '--close-branch', '-m', 'Closing before')
    repo.hg('update', 'default')
    repo.hg('merge', 'gnu')
    repo.hg('commit', '-m', "Merged gnu into default through CLI")
    if close == 'close-after':
        repo.hg('update', 'gnu')
        repo.hg('commit', '--close-branch', '-m', 'Closing after')
    repo.hg('phase', '-p', '.')
    repo.hg('push')
    print("Graph after CLI merge:")
    print(repo.graphlog(hidden=True))
    mr.wait_assert_merged(expected_source_branch=gl_branch,
                          check_source_branch_removal=(close != 'no-close'))

    # Commit list is correct
    mr.assert_commit_link("Le lion est prédateur", head_sha)


def test_mergerequest_cli_named_branch_slash(public_project, tmpdir):
    """Test for forward slash in branch name.

    More than just the MR, this tests also regular Mercurial operation,
    see heptapod#133
    """
    repo = hg.LocalRepo.init(tmpdir.join('repo'),
                             default_url=public_project.owner_basic_auth_url)
    branch = 'gr/gnu'
    prepare_named_branch(repo, branch_name=branch)
    mr = MergeRequest.api_create(public_project,
                                 source_branch=gitlab_branch(branch),
                                 target_branch=gitlab_branch('default'))

    repo.hg('update', 'default')
    repo.hg('merge', 'gr/gnu')
    repo.hg('commit', '-m', "Merged gr/gnu into default through CLI")
    repo.hg('push', '-r', '.', '--pub')
    print("Graph after API merge:")
    print(repo.graphlog(hidden=True))
    mr.wait_assert_merged(check_source_branch_removal=False)


def test_mergerequest_child_amend_publish(test_project, tmpdir):
    """Here we produce a child, amend it, then push/publish in one shot.

    This case is interesting because Heptapod could well never associate
    the child with the merge request.
    """
    repo = hg.LocalRepo.init(tmpdir.join('repo'),
                             default_url=test_project.owner_basic_auth_url)
    topic = prepare_topic(repo, needing_rebase=False)
    mr = api_create_mr(test_project, topic=topic)

    repo.path.join('horse').write("A lion is stronger than a horse\n")
    repo.hg('commit', '-Am', "Even a horse!")
    repo.hg('amend', '-d', "2001-01-01")
    head_sha = repo.node('.')
    print("Graph before push/publish:")
    print(repo.graphlog(hidden=True))
    # forcing is necessary with client-side Mercurial 6.4.1 / hg-evolve 11.0.1
    # This looks like a bug in evolve or topic. Wasn't needed with 6.3.3 and
    # 10.5.3
    repo.hg('push', '--publish', '-f')
    print("Graph after push/publish:")
    print(repo.graphlog())
    mr.wait_assert_merged()

    # Commit list is correct
    mr.assert_commit_link("Even a horse", head_sha)


def test_mergerequest_api_obsolete_multiple_heads(public_project, tmpdir):
    """Reproduction for heptapod#86

    This is based on the api_explicit_merge scenario, to which we add
    an obsolete server-side head on the 'default' branch.

    No topic is set on the obsolete head, even though I've seen some obsolete
    heads with topics involved in the original case reported as heptapod#86,
    because this would arguably be a Mercurial bug, that could independently
    be fixed in a later version (makes me think of the one behind heptapod#43)

    The chosen way to create the remote obsolete head is to obsolete the
    existing one and add a new visible head. For that, we need to lift the
    auto-publishing of non-topic drafts in the first place.
    """
    public_project.api_hgrc_set(inherit=True, auto_publish='nothing')
    repo = hg.LocalRepo.init(tmpdir.join('repo'),
                             default_url=public_project.owner_basic_auth_url)
    topic = prepare_topic(repo)
    topic_sha = repo.node(topic)
    repo.hg('prune', '-r', 'default')
    repo.hg('up', '0')
    repo.path.join('zebra').write("A lion is stronger than a zebra\n")
    repo.hg('commit', '-Am', "Even a zebra!")
    repo.hg('push')

    mr = api_create_mr(public_project, topic=topic)
    mr.api_accept()

    repo.hg('pull')
    # we don't have wild heads
    # Before hg-git@8fb455e99dc7 this used to be hard error, meaning
    # that experimental.single-head-per-branch rightfully did not consider the
    # obsolete head, but hg-git did.
    public_project.wait_assert_api_branches(
        lambda branches: set(branches) == {'branch/default'})

    print("Graph after API merge:")
    print(repo.graphlog(hidden=True))
    log = repo.hg('log', '-T', '{desc|firstline}:{phase}\n')
    assert log.splitlines() == [
        "Merge branch 'topic/default/antelope' into 'branch/default':public",
        "Even a zebra!:public",
        "Même une antilope !:public",
        "Initial sentence:public",
    ]

    # Commit list is correct (recall that zebra is in the target branch)
    mr.assert_commit_link("Même une antilope !", topic_sha)


@parametrize('change_meth', ('api_change', 'webui_change'))
@parametrize('merge_meth', ('api_merge', 'rebase_push'))
def test_mergerequest_change_source(
        test_project, tmpdir, change_meth, merge_meth):
    """Test for changing source GitLab branch of a MR (heptapod#138)
    """
    repo = hg.LocalRepo.init(tmpdir.join('repo'),
                             default_url=test_project.owner_basic_auth_url)
    topic = prepare_topic(repo)
    mr = api_create_mr(test_project, topic=topic)
    # make sure the first mergeability checks are done so that they
    # don't interfere with the ones related to the actual test.
    # remove this if we add something able to force recheck after all
    # pending async checks are done (lease-based retry?)
    mr.wait_assert(lambda info: info.get('merge_status') == 'can_be_merged')

    new_topic = 'cloven'
    repo.hg('topic', new_topic)
    # changing title to be easily sure the MR refresh worked well
    repo.hg('amend', '-m', "all cloven-hoofed")
    repo.hg('push', '-r', '.')

    # we don't want to reopen  in concurrency with the async job that closes it
    mr.wait_assert(
        lambda info: info.get('state') == 'closed')

    new_source_branch = 'topic/default/' + new_topic
    edit_payload = dict(state_event='reopen')
    if change_meth == 'api_change':
        edit_payload['source_branch'] = new_source_branch
    elif change_meth == 'webui_change':
        webdriver = test_project.owner_webdriver
        # See heptapod#1212
        with window_size(webdriver, 1920, 1080):
            webdriver.get(mr.url + '/edit')
            wait_could_click_button(
                webdriver,
                data_field_name='merge_request[source_branch]')
            wait_could_click(
                webdriver, By.XPATH,
                '//div[contains(@class, "js-source-branch-dropdown")]'
                '//a[@data-branch="%s"]' % new_source_branch)
            wait_could_click_button(webdriver, data_track_label='submit_mr')

    mr_info = mr.api_edit(**edit_payload)
    assert mr_info.get('source_branch') == new_source_branch
    mr.assert_commit_link("cloven-hoofed", repo.node('cloven'))

    if merge_meth == 'rebase_push':
        rebase_publish_push(repo, new_topic)
    else:
        mr.api_accept(check_merged=False, timeout_factor=3)

    # and merge has been detected
    mr.wait_assert_merged(timeout_factor=3)
