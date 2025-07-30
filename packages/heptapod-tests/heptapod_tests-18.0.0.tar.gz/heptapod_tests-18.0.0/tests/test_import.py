# -*- coding: utf-8 -*-
import pytest
from heptapod_tests.content import (
    prepare_import_source_git,
    prepare_import_source_hg,
)
from heptapod_tests.hg import (
    assert_matching_changesets,
    LocalRepo,
)
from heptapod_tests.project import Project
from heptapod_tests.utils import unique_name

parametrize = pytest.mark.parametrize


@parametrize('method', ['api', 'webdriver'])
def test_import_basic(public_project, tmpdir, method):
    """Test import, using Heptapod instance itself as source."""

    heptapod = public_project.heptapod
    src_repo, src_url = prepare_import_source_hg(public_project, tmpdir,
                                                 tweak_hgrc=False)
    print("Graph of source project after push:")
    print(src_repo.graphlog())

    project_name = unique_name('test_import')
    if method == 'api':
        importer = Project.api_import_url
        options = {}
    else:
        importer = Project.webdriver_import_url
        options = dict(wait_import_url_validation=True)

    with importer(
        heptapod,
        user=heptapod.get_user('test_basic'),
        project_name=project_name,
        url=src_url,
        **options,
    ) as project:
        clone = LocalRepo.clone(project.owner_basic_auth_url,
                                tmpdir.join('repo'))
        assert_matching_changesets(clone, src_repo,
                                   ('node', 'desc', 'topic'),
                                   ordered=False)
        assert project.api_default_branch() == 'branch/default'


def test_webdriver_import_error_remote_404(public_project, tmpdir):
    heptapod = public_project.heptapod
    src_repo, src_url = prepare_import_source_hg(public_project, tmpdir,
                                                 tweak_hgrc=False)
    user = heptapod.get_user('test_basic')

    with Project.webdriver_import_url(
            heptapod,
            user=user,
            project_name=unique_name('import_errors'),
            check_success=False,
            vcs_type='hg',
            # here is the error:
            url=src_url.replace('public_project', 'no_such_project'),
    ) as project:
        if project is None:
            Project.webdriver_assert_import_form_url_error(
                user.webdriver,
                expected='not a valid repository of the specified '
                'VCS type at this URL')
            return

        info = project.api_get_info()
        assert info['import_status'] == 'failed'
        # TODO would be nice to have an error message making the
        # difference between "not a Mercurial repo" and "URL does not exist"
        # (404) or more transient problems

        error_title, error_body = project.webdriver_import_errors()
        assert "could not be imported" in error_title

        # As of GitLab 15.11, there does not seem to be an API endpoint
        # that makes the distinction between empty repository and no
        # repository, so we go the webdriver way.
        project.webdriver_assert_no_repo(check_buttons=True)


def test_webdriver_import_error_remote_is_git(git_project, tmpdir):
    heptapod = git_project.heptapod

    user = heptapod.get_user('test_basic')

    src, external_url = prepare_import_source_git(git_project, tmpdir)

    with Project.webdriver_import_url(
            heptapod,
            user=user,
            project_name=unique_name('import_errors'),
            check_success=False,
            url=external_url,
            # here is the error: VCS type mismatch
            vcs_type='hg',
    ) as project:
        if project is None:
            Project.webdriver_assert_import_form_url_error(
                user.webdriver,
                expected='not a valid repository of the specified '
                'VCS type at this URL')
            return

        info = project.api_get_info()
        assert info['import_status'] == 'failed'
        error_msg = info['import_error']
        expected_msg = "not a valid HTTP Mercurial repository"
        assert expected_msg in error_msg

        error_title, error_body = project.webdriver_import_errors()
        assert "could not be imported" in error_title

        assert expected_msg in error_msg

        # As of GitLab 15.11, there does not seem to be an API endpoint
        # that makes the distinction between empty repository and no
        # repository.
        project.webdriver_assert_no_repo(check_buttons=True)


def test_import_non_topic_draft(public_project, tmpdir):
    """Draft non topic changesets should not been published by import."""

    heptapod = public_project.heptapod
    src_repo, src_url = prepare_import_source_hg(public_project, tmpdir)
    print("Graph of source project after push:")
    print(src_repo.graphlog())

    project_name = unique_name('test_import')

    with Project.api_import_url(
        heptapod,
        user=heptapod.get_user('test_basic'),
        project_name=project_name,
        url=src_url,
    ) as project:
        clone = LocalRepo.clone(project.owner_basic_auth_url,
                                tmpdir.join('repo'))
        assert clone.hg('log', '-T', '{phase}', '-r', 0) == 'draft', (
            "draft non-topic changeset should not become public "
            "in imported repo")
        assert_matching_changesets(clone, src_repo,
                                   ('node', 'desc', 'topic', 'phase'),
                                   ordered=False)
        assert project.api_default_branch() == 'branch/default'


def test_import_multiple_heads(public_project, tmpdir):
    """Test import, using Heptapod instance itself as source."""

    heptapod = public_project.heptapod
    src_repo, src_url = prepare_import_source_hg(public_project, tmpdir)

    # Now let's make a new wild head
    src_repo.hg('up', '0')
    src_repo.path.join('sea').write("A whale is stronger than a shrimp\n")
    src_repo.hg('commit', '-Am', "Started listing sea animals")
    src_repo.hg('push', '-f')
    print("Graph of source project after push:")
    print(src_repo.graphlog())

    project_name = unique_name('test_import')

    with Project.api_import_url(
        heptapod,
        user=heptapod.get_user('test_basic'),
        project_name=project_name,
        url=src_url,
    ) as project:
        clone = LocalRepo.clone(project.owner_basic_auth_url,
                                tmpdir.join('repo'))
        assert_matching_changesets(clone, src_repo,
                                   ('node', 'desc', 'topic', 'phase'),
                                   ordered=False)


def test_import_bookmarks(public_project, tmpdir):
    """Test import, using Heptapod instance itself as source."""

    heptapod = public_project.heptapod
    src_repo, src_url = prepare_import_source_hg(public_project, tmpdir)

    # Now let's put a bookmark on a non topic changeset
    src_repo.hg('bookmark', '-r', '1', 'book1')
    src_repo.hg('push', '-B', 'book1', expected_return_code=1)

    print("Graph of source project after push:")
    print(src_repo.graphlog())

    project_name = unique_name('test_import')

    with Project.api_import_url(
        heptapod,
        user=heptapod.get_user('test_basic'),
        project_name=project_name,
        url=src_url,
    ) as project:
        clone = LocalRepo.clone(project.owner_basic_auth_url,
                                tmpdir.join('repo'))
        assert_matching_changesets(clone, src_repo,
                                   ('node', 'desc', 'phase', 'bookmarks'),
                                   ordered=False)
