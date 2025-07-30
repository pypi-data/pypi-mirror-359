"""Tests for repository file read/write through the Rails app.

We're mostly using the public_project because it belongs to `basic_user`
whose name if full of non ASCII characters.
"""
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from heptapod_tests.access_levels import ProjectAccess

from heptapod_tests.hg import LocalRepo
from heptapod_tests.project import (
    branch_title,
)
from heptapod_tests.selenium import (
    wait_could_click,
    wait_could_click_button,
    wait_element_visible,
)
parametrize = pytest.mark.parametrize


@parametrize('topic', ['topic', 'non-topic'])
def test_create_file_on_existing_gitlab_branch(public_project, tmpdir, topic):
    # direct boolean values are obscure in test summaries, hence:
    topic = topic == 'topic'
    proj = public_project
    url = proj.owner_basic_auth_url
    repo_path = tmpdir.join('repo1')
    repo = LocalRepo.init(repo_path)

    repo_path.join('foo').write('foo0')
    repo.hg('commit', '-Am', "Commit 0")
    repo.hg('phase', '-p', ".")
    if topic:
        repo.hg('topic', 'ze-top')
        repo_path.join('foo').write('foo1')
        repo.hg('commit', '-Am', "Commit 1")
    repo.hg('push', url)

    gitlab_branch = 'topic/default/ze-top' if topic else 'branch/default'
    log_rev = 'ze-top' if topic else 'default'
    expected_phase = 'draft' if topic else 'public'

    readme = "# Please read me"
    proj.api_file_create('README.md',
                         branch=gitlab_branch,
                         start_branch=gitlab_branch,
                         content=readme,
                         commit_message="README TTW",
                         )
    assert proj.api_branch_titles().get(gitlab_branch) == 'README TTW'

    clone_path = tmpdir.join('repo2')
    clone = LocalRepo.clone(url, clone_path)
    if topic:
        clone.hg('up', log_rev)
    log = clone.hg('log', '-r', log_rev, '-T', '{desc}:{phase}')
    assert log.strip() == 'README TTW:' + expected_phase

    assert clone_path.join('README.md').read() == "# Please read me"

    content = proj.api_file_get('README.md', gitlab_branch)
    assert content == b"# Please read me"
    # updates giving an empty diff are not errors
    proj.api_file_update('README.md',
                         branch=gitlab_branch,
                         start_branch=gitlab_branch,
                         content=readme,
                         commit_message="README TTW empty diff",
                         )

    # Now let's update an existing file, not the one we created
    proj.api_file_update('foo',
                         branch=gitlab_branch,
                         start_branch=gitlab_branch,
                         content="foo1\nfoo2",
                         commit_message="Foo TTW",
                         )
    assert proj.wait_assert_api_branches(
        lambda branches: branch_title(branches, gitlab_branch) == 'Foo TTW',
    )
    clone.hg('pull', url, '-u')
    assert clone_path.join('foo').read_binary() == b"foo1\nfoo2"

    # Finally let's remove a file (note: move without sending content does
    # not seem to be supported in this API endpoint)
    proj.api_file_delete('foo',
                         branch=gitlab_branch,
                         commit_message="Bye, you fool",
                         )
    proj.wait_assert_api_branches(
        lambda branches: branch_title(branches,
                                      gitlab_branch) == 'Bye, you fool',
    )
    clone.hg('pull', url, '-u')
    assert not clone_path.join('foo').exists()


def test_empty_repo_file_create_update(test_project):
    proj = test_project
    gitlab_branch = 'branch/default'
    path = 'README.md'
    proj.api_file_create(path,
                         content="# Please read me",
                         branch=gitlab_branch,
                         commit_message="README TTW")
    assert proj.api_file_get(path, gitlab_branch) == b'# Please read me'

    proj.api_file_update(path,
                         content="# An update",
                         branch=gitlab_branch,
                         commit_message="Update TTW")
    assert proj.api_file_get(path, gitlab_branch) == b'# An update'

    resp = proj.api_file_create(path,
                                content="# Should have been an update",
                                branch=gitlab_branch,
                                commit_message="Wrong TTW update",
                                check=False)
    assert resp.status_code == 400
    assert 'already exists' in resp.json()['message']


def test_create_file_publisher_permission(test_project, tmpdir):
    proj = test_project
    repo_path = tmpdir.join('repo1')
    repo = LocalRepo.init(repo_path, default_url=proj.owner_basic_auth_url)

    repo_path.join('foo').write('foo0')
    repo.hg('commit', '-Am', "Commit 0")
    # ensures that the (protected) default GitLab branch is 'branch/default'
    repo.hg('push', '--publish')

    basic_user = test_project.heptapod.get_user('test_basic')
    test_project.grant_member_access(user=basic_user,
                                     level=ProjectAccess.DEVELOPER)
    test_project.wait_assert_user_visible(basic_user)

    resp = test_project.api_file_create(user=basic_user,
                                        check=False,
                                        branch='branch/other',
                                        start_branch='branch/default',
                                        path='bar',
                                        content="Boor",
                                        commit_message="will be rejected")
    assert resp.status_code == 403
    msg = resp.json()['message']
    assert "public changeset" in msg
    assert "branch 'other'" in msg

    topic = 'topic/other/bar'
    test_project.api_file_create(user=basic_user,
                                 branch=topic,
                                 start_branch='branch/default',
                                 path='bar',
                                 content="Boor",
                                 commit_message="Topic creating branch works")
    assert proj.api_file_get('bar', topic) == b"Boor"
    # reproduction of heptapod#714
    assert proj.api_default_branch() == 'branch/default'


def prepare_for_updates(proj, repo_path):
    repo = LocalRepo.init(repo_path, default_url=proj.owner_basic_auth_url)

    (repo_path / 'unix').write_binary(b'line1\nline2')
    (repo_path / 'windows').write_binary(b'line1\r\nline2')
    (repo_path / 'macos_classic').write_binary(b'line1\rline2')
    repo.hg('commit', '-Am', "Commit 0")
    # publishing ensures that we don't have surprises with the default
    # GitLab branch
    repo.hg('push', '--publish')
    return repo


def test_webdriver_update_file_eols(test_project, tmpdir):
    repo_path = tmpdir.join('repo1')
    repo = prepare_for_updates(test_project, repo_path)
    webdriver = test_project.owner_webdriver

    for file_name in ('unix', 'windows', 'macos_classic'):
        webdriver.get('/'.join(
            (test_project.url, '-', 'edit', 'branch/default', file_name)))
        textarea = wait_element_visible(
            webdriver, By.XPATH, '//div[@id="editor"]//textarea')
        textarea.send_keys('from the web')
        textarea.send_keys(Keys.RETURN)

        wait_could_click_button(webdriver,
                                data_testid='blob-edit-header-commit-button')
        wait_could_click_button(
            webdriver, data_testid='commit-change-modal-commit-button')
        # "Your changes have been committed successfully" alert, but
        # "changes" being a link, we need to access the second text fragment
        # to query something meaningful
        wait_element_visible(webdriver, By.XPATH,
                             '//div[contains(@class, "gl-alert-body") '
                             'and contains(text()[2], "have been committed")]')

    # Actually, the committing we just did still looks to be synchronous,
    # but we can as well be ready for when it's not anymore.
    repo.wait_pull_new_changesets(3, '-u')

    assert (repo_path / 'unix').read_binary() == (
        b'from the web\n'
        b'line1\n'
        b'line2'
    )
    assert (repo_path / 'windows').read_binary() == (
        b'from the web\r\n'
        b'line1\r\n'
        b'line2'
    )
    # not testing MacOS Classic anymore: GitLab frontend now takes care of
    # Windows vs Unix, making it harder to also treat `\r` line endings. It
    # also sends the fixed payload as if it were a file upload now, making
    # it impossible from the controller to behave differently in the web edit
    # and file upload cases.
    # The MacOS line endings have always be for completeness, and hopefully
    # nobody cares.

    # A direct file upload must *not* preserve end of lines.
    # Rationale:
    # - it's reasonable to expect the file to be exactly what the user wants
    # - the file can be binary.
    replacement_path = tmpdir / 'replacement'
    replacement_bin = b"yes,\r\nwe really want windows line endings here"
    replacement_path.write_binary(replacement_bin)

    webdriver.get('/'.join(
        (test_project.url, '-', 'blob', 'branch/default', 'unix')))
    wait_could_click(webdriver, By.XPATH,
                     '//div[@data-testid="blob-overflow-menu"]/button')
    wait_could_click_button(webdriver, data_testid='replace', timeout_factor=3)

    wait_could_click(webdriver, By.XPATH, '//p[@data-testid="upload-text"]/a')

    uploader = webdriver.find_elements(By.XPATH, '//input[@type="file"]')[0]
    uploader.send_keys(str(replacement_path))

    wait_could_click(webdriver, By.CSS_SELECTOR,
                     'footer.modal-footer button.btn-confirm')

    # CR/LF has not been rewritten to just LF
    # async behavior witnessed in the case of the file upload
    repo.wait_pull_new_changesets(1, '-u')
    assert (repo_path / 'unix').read_binary() == replacement_bin
