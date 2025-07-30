from io import BytesIO
import os
import pytest
import requests
import time
from selenium.common.exceptions import (
    NoSuchElementException,
)
from selenium.webdriver.common.by import By
import tarfile

from heptapod_tests.utils import (
    unique_name,
)
from heptapod_tests.access_levels import (
    GroupAccess,
    ProjectAccess,
)
from heptapod_tests.project import (
    Project,
)
from heptapod_tests.namespace import Group
from heptapod_tests.git import LocalRepo as GitRepo
from heptapod_tests.hg import LocalRepo
from heptapod_tests.selenium import (
    wait_could_click,
    wait_could_click_button,
    wait_element_visible,
    webdriver_wait,
)
from heptapod_tests.wait import wait_assert

from .constants import DATA_DIR
from . import needs

parametrize = pytest.mark.parametrize


@parametrize('init_repo', ['with_readme', 'without_readme'])
def test_webdriver_create(heptapod, tmpdir, init_repo):
    """Create a project through the Web UI and check basic operation."""
    init_with_readme = init_repo == 'with_readme'
    with Project.webdriver_create(heptapod, 'test_basic',
                                  unique_name('test_create'),
                                  init_with_readme=init_with_readme,
                                  ) as project:
        # Empty page (instructions)
        webdriver = project.owner_webdriver
        webdriver.get(project.url)

        repo_path = tmpdir.join('repo1')
        project_url = project.owner_basic_auth_url
        if init_with_readme:
            repo = LocalRepo.clone(project_url, repo_path)
            Extract, extracts = repo.changeset_extracts((
                'phase', 'branch', 'topic', 'bookmarks'))
            assert len(extracts) == 1
            assert extracts[0] == Extract(phase='public',
                                          branch='default',
                                          topic='',
                                          bookmarks='')
            assert repo.hg('files').splitlines() == ['README.md']
        else:
            # testing empty repo page
            assert "hg clone" in webdriver.page_source
            repo = LocalRepo.init(repo_path, default_url=project_url)

        # A push works
        repo_path.join('foo').write('foo0')
        repo.hg('commit', '-Am', "Commit 0")
        repo.hg("push")

        project.wait_assert_api_branch_titles({'branch/default': 'Commit 0'})
        # webdriver.title was before that just telling that the default
        # branch is undefined.
        webdriver.refresh()
        assert project.name in webdriver.title


def test_transfer(public_project, tmpdir):
    """Basic test of transfer, does not care about HGRC inheritance.

    HGRC inheritance under transfers is tested in the test_groups module.
    """
    inner_test_transfer(public_project, tmpdir)


@needs.services
@needs.docker
def test_transfer_not_hashed(public_project, tmpdir):
    public_project.make_storage_legacy()
    inner_test_transfer(public_project, tmpdir)


def inner_test_transfer(public_project, tmpdir):
    proj = public_project
    repo_path = tmpdir.join('repo1')

    repo = LocalRepo.init(repo_path)
    repo_path.join('foo').write('foo0')
    repo.hg('commit', '-Am', "Commit 0")
    repo.hg('phase', '-p', ".")
    repo.hg('push', proj.owner_basic_auth_url)
    with Group.api_create(proj.heptapod,
                          unique_name('test_group'),
                          user_name='test_basic') as group:
        resp = proj.api_transfer(group)
        assert resp.status_code < 400

        url = proj.owner_basic_auth_url
        assert 'test_group' in url  # avoid false positives

        # we can clone the transfered project
        clone = LocalRepo.clone(url, tmpdir.join('repo2'))
        log = clone.hg('log', '-T', '{desc}:{phase}:{topic}\n')
        assert log.splitlines() == ['Commit 0:public:']

        # and push new changesets
        clone.path.join('foo').write('foo1')
        clone.hg('commit', '-Am', "Commit 1")
        clone.hg('phase', '-p', ".")
        # clone does not store passwords in paths
        clone.hg('push', proj.owner_basic_auth_url)

        # let's check what GitLab sees
        assert proj.api_branch_titles() == {'branch/default': 'Commit 1'}


def test_rename(test_project, tmpdir):
    """Test that hard rename (change of slug, aka path) works."""
    proj = test_project
    orig_url = proj.owner_basic_auth_url
    repo_path = tmpdir.join('repo1')

    repo = LocalRepo.init(repo_path)
    repo_path.join('foo').write('foo0')
    repo.hg('commit', '-Am', "Commit 0")
    repo.hg('phase', '-p', ".")
    repo.hg('push', orig_url)

    new_path = unique_name('renamed')
    proj.api_edit(path=new_path)

    proj.name = new_path  # for our test helper
    url = proj.owner_basic_auth_url
    assert 'renamed' in url  # avoid false positives

    # we can clone the renamed project
    clone = LocalRepo.clone(url, tmpdir.join('repo2'))
    log = clone.hg('log', '-T', '{desc}:{phase}:{topic}\n')
    assert log.splitlines() == ['Commit 0:public:']

    # and push new changesets
    clone.path.join('foo').write('foo1')
    clone.hg('commit', '-Am', "Commit 1")
    clone.hg('phase', '-p', ".")
    # clone does not store passwords in paths
    clone.hg('push', proj.owner_basic_auth_url)

    # let's check what GitLab sees
    assert proj.api_branch_titles() == {'branch/default': 'Commit 1'}

    # Starting with GitLab 10.3, we have a redirection
    assert 'renamed' not in orig_url  # to be sure of what we are testing
    resp = requests.get(orig_url, allow_redirects=False)
    # response is actually 302, but that may change
    assert resp.status_code in (301, 302, 303)

    # Pull on the old URL is redirected
    repo.hg('pull', orig_url)
    log = repo.hg('log', '-T', '{desc}:{phase}\n')
    assert log.splitlines() == ['Commit 1:public', 'Commit 0:public']


def test_403(test_project):
    """Test that unauthorized commands give rise to a 403.

    As of this writing, all these functional tests are run with the
    administrator account, hence we have to rely on the fact that
    unknown commands currently trigger an Unauthorized. If they become
    NotFound errors in the future, we'll have to revise this, and hopefully
    we'll have several authentications at this point.
    """
    resp = test_project.owner_get(params=dict(cmd='nosuchcmd'))
    assert resp.status_code == 403


def test_cli_404(test_project):
    """Test that hg CLI gets a 404 if repo does not exist or isn't visible.

    """
    heptapod = test_project.heptapod
    user = 'test_basic'
    basic_user_creds = (user, heptapod.users[user].password)

    resp = requests.get(heptapod.url + '/no/such/project?cmd=capabilities',
                        auth=basic_user_creds)
    assert resp.status_code == 404

    resp = requests.get(test_project.url + '?cmd=capabilities',
                        auth=basic_user_creds)
    assert resp.status_code == 404


def test_graphql(test_project):
    # Model attribute / column name has to be switched from snake_case to
    # mixedCamelCase
    fields = test_project.graphql_get_fields(['vcsType'])
    assert fields == dict(vcsType=test_project.vcs_type,
                          )


@needs.hg_native  # arbitrary, just to avoid running it several times in CI
def test_project_image_file(public_project):
    """Reproduction of omnibus-heptapod#22.

    Not in test_python_gitlab.py because it's not intended to check
    that python-gitlab works with Heptapod, it's just relying on python-gitlab
    because we found the issue by running Heptapod API Import.

    Using the public project because it nakes dowload check easier. Problem
    was first encountered on a public project anyway (it does not matter).
    """
    proj = public_project
    api_client = proj.owner_user.python_gitlab_client
    api_project = api_client.projects.get(proj.id)
    filename = 'small.jpg'
    data_path = DATA_DIR / filename
    uploaded = api_project.upload(filename, filepath=data_path)
    uri = uploaded['url']
    resp = requests.get(proj.heptapod.url + f'/-/project/{proj.id}' + uri)
    assert resp.status_code == 200
    assert resp.headers['Content-Type'] == 'image/jpeg'
    # arbitrary, result is changed by EXIF stripping done by Workhorse
    assert len(resp.content) > 400


def test_hgrc_get_put(test_project):
    resp = test_project.owner_api_hgrc_get()
    assert resp.status_code == 200
    assert resp.json() == dict(inherit=True)

    resp = test_project.owner_api_hg_heptapod_config()
    assert resp.status_code == 200
    assert resp.json() == {}

    resp = test_project.api_hgrc_set(inherit=True,
                                     auto_publish='nothing')
    assert resp.status_code == 204

    resp = test_project.owner_api_hgrc_get()
    assert resp.status_code == 200
    assert resp.json() == dict(inherit=True, auto_publish='nothing')

    resp = test_project.owner_api_hg_heptapod_config()
    assert resp.status_code == 200
    assert resp.json() == {'auto-publish': 'nothing'}

    # api PUT adds new settings
    resp = test_project.api_hgrc_set(inherit=True,
                                     allow_bookmarks=True)
    assert resp.status_code == 204
    resp = test_project.owner_api_hg_heptapod_config()
    assert resp.status_code == 200
    assert resp.json() == {'allow-bookmarks': True,
                           'auto-publish': 'nothing',
                           }
    # not passing inherit does not change it
    resp = test_project.api_hgrc_set(inherit=True,
                                     allow_bookmarks=False)
    assert resp.status_code == 204
    resp = test_project.owner_api_hg_heptapod_config()
    assert resp.status_code == 200
    assert resp.json() == {'allow-bookmarks': False,
                           'auto-publish': 'nothing',
                           }

    # changing inheritance
    resp = test_project.api_hgrc_set(inherit=False)
    assert resp.status_code == 204
    resp = test_project.owner_api_hgrc_get()
    assert resp.status_code == 200
    assert resp.json()['inherit'] is False

    # getting back to the defaults
    resp = test_project.owner_api_hgrc_reset()
    assert resp.status_code == 204
    resp = test_project.owner_api_hgrc_get()
    assert resp.status_code == 200
    as_json = resp.json()
    assert as_json['inherit'] is True

    # TODO after heptapod#301, last update info are not provided
    # any more. Would be nice to get it back.


@needs.services
@needs.docker
def test_hashed_storage_migration(heptapod, tmpdir):

    user_name = 'test_basic'

    repo_path = tmpdir.join('repo1')
    repo = LocalRepo.init(repo_path)
    repo_path.join('foo').write('foo0')
    repo.hg('commit', '-Am', "Commit 0")
    repo.hg('phase', '-p', ".")
    repo.hg('topic', 'zetop')
    repo_path.join('foo').write('foo1')
    repo.hg('commit', '-Am', "Commit 1")

    # we'll make a group for ease of use of `group.put_hgrc`
    # the same scenario should work identically otherwise with personal
    # namespaces
    group_name = unique_name('test_hash_migr')
    with Group.api_create(heptapod, group_name, user_name=user_name) as group:
        group.put_hgrc(("[experimental]\n",
                        "groupconf=test\n"))
        project = Project.api_create(heptapod, user_name, 'proj', group=group)
        url = project.owner_basic_auth_url
        repo.hg('push', url)

        # on GitLab 13, all new projects are on the hashed storage, so
        # let's test the rollback first.
        # This asserts that the project is at its expected new location.
        project.make_storage_legacy()

        # HGRC inheritance is still there
        assert project.hg_config('experimental')['groupconf'] == 'test'

        # Project repo works
        clone = LocalRepo.clone(url, tmpdir.join('legacy'))
        log = clone.hg('log', '-T', '{desc}:{phase}:{topic}\n')
        assert log.splitlines() == ['Commit 1:draft:zetop', 'Commit 0:public:']
        repo_path.join('foo').write('foo2')
        repo.hg('amend', '-m', "Commit 2")
        repo.hg('push', url)
        assert project.api_branch_titles() == {
            'branch/default': 'Commit 0',
            'topic/default/zetop': 'Commit 2',
        }
        clone.hg('pull')
        log = clone.hg('log', '-T', '{desc}:{phase}:{topic}\n')
        assert log.splitlines() == ['Commit 2:draft:zetop', 'Commit 0:public:']

        # now let's go for the migration to hashed
        project.make_storage_hashed()

        # HGRC inheritance is still there
        assert project.hg_config('experimental')['groupconf'] == 'test'

        # Project repo works
        clone = LocalRepo.clone(url, tmpdir.join('migrated'))
        log = clone.hg('log', '-T', '{desc}:{phase}:{topic}\n')
        assert log.splitlines() == ['Commit 2:draft:zetop', 'Commit 0:public:']

        repo_path.join('foo').write('foo3')
        repo.hg('amend', '-m', "Commit 3")
        repo.hg('push', url)
        assert project.api_branch_titles() == {
            'branch/default': 'Commit 0',
            'topic/default/zetop': 'Commit 3',
        }
        clone.hg('pull')
        log = clone.hg('log', '-T', '{desc}:{phase}:{topic}\n')
        assert log.splitlines() == ['Commit 3:draft:zetop', 'Commit 0:public:']


@needs.services
def test_housekeeping(test_project):
    heptapod = test_project.heptapod
    out = heptapod.rake('gitlab:git:force_housekeeping',
                        'PROJECT_ID=%d' % test_project.id)
    # This proves there was no error (rake does not exit with error code
    # or at least, it's very uncommon in the rake culture)
    assert any(b"Done." in l for l in out.splitlines())

    # making sure the API is not broken, but we can't assert much because
    # it's run async and decides by itself what to do.
    resp = test_project.api_post(subpath='housekeeping')
    assert resp.status_code == 201


@needs.hg_native
@parametrize('how', ['bumped-quota', 'group-member'])
def test_external_user_can_create_project(how, test_group, external_user):
    heptapod = test_group.heptapod
    webdriver = external_user.webdriver

    # if the external user has no group, there's no link to create a project.
    # note that the "+" menu title itself is such a link
    # (disabled by JavaScript), even if the dropdown doesn't have the
    # "New project" option, so we must avoid a false negative here.
    dashboard_new_proj_link_sel = (
        By.XPATH,
        '//a[@href="/projects/new" and @data-testid="new-project-button"]'
    )
    with pytest.raises(NoSuchElementException):
        webdriver.find_element(*dashboard_new_proj_link_sel)

    if how == 'bumped-quota':
        external_user.edit(projects_limit=1)
    elif how == 'group-member':
        test_group.grant_member_access(external_user,
                                       GroupAccess.DEVELOPER)

    # Now we have this big link in the middle of the page
    webdriver.get(heptapod.url)
    try:
        wait_element_visible(webdriver, *dashboard_new_proj_link_sel)
        link = webdriver.find_element(*dashboard_new_proj_link_sel)
        assert link.is_enabled()
    except NoSuchElementException:
        raise AssertionError("Button link to projects page creation "
                             "not on personal dashboard")

    # Navigation to Project creation page via dropdown menu (plus sign, "+")
    # As of GitLab 16.1, the menu is not displayed on mobile.
    # (transient webdriver, so we don't bother restoring the size afterwards)
    webdriver.set_window_size(1920, 1080)
    wait_could_click(webdriver, By.XPATH,
                     '//div[@data-testid="new-menu-toggle"]')
    wait_could_click(webdriver, By.XPATH,
                     '//a[@href="/projects/new" '
                     'and @data-qa-create-menu-item="general_new_project"]')
    assert webdriver.current_url == heptapod.url + '/projects/new'

    wait_could_click(webdriver, By.XPATH, '//a[@href = "#blank_project"]')

    if how == 'group-member':
        namespace = test_group
        # The default selected namespace is test_group
        # (hoping its id won't change too much with GitLab versions)
        namespace_select_id = 'project_namespace_id'
        webdriver_wait(webdriver).until(
            lambda d: d.find_element(By.ID, namespace_select_id).is_displayed)
        namespace_select = webdriver.find_element(By.ID, namespace_select_id)
        assert namespace_select.get_attribute('value').strip() == str(
            test_group.id)
    elif how == 'bumped-quota':
        namespace = external_user.personal_namespace
        # creation in personal namespace is the only possibility.
        # Page structure is different
        namespace_elt = webdriver.find_element(By.CSS_SELECTOR,
                                               '.input-group-text')
        webdriver_wait(webdriver).until(
            lambda _: namespace_elt.is_displayed)
        assert namespace_elt.text.strip().rstrip('/') == namespace.url

    project = None
    try:
        Project.webdriver_new_project_submit(webdriver, 'ext_create',
                                             vcs_type=heptapod.vcs_type)
        # external_user doesn't have an access token, making one just to
        # use it once would be too costly.
        project = Project.api_retrieve(heptapod, 'root', namespace,
                                       'ext_create')
        assert (project.owner == external_user.name
                or project.creator_id == external_user.id)
    finally:
        if project is not None:
            # in the group case, user doesn't have the right to delete
            # the project
            project.api_destroy(as_user='root')


def test_archive(public_project, tmpdir):
    repo_path = tmpdir.join('repo1')

    repo = LocalRepo.init(repo_path,
                          default_url=public_project.owner_basic_auth_url)
    repo_path.join('foo').write('archived')
    repo.hg('commit', '-Am', "Commit 0")
    node = repo.node('.')
    repo.hg('push')

    # python 3.9 apparently has a nicer syntax for multi-line with statements
    # (not worth requiring it right away, of course)
    # https://bugs.python.org/issue12782
    with public_project.get_archive('branch/default') as arch_file, \
            tarfile.open(fileobj=arch_file) as tarf:
        toc = tarf.getnames()
        main_dir = toc[0].split('/', 1)[0]
        assert set(toc) == {main_dir + '/.hg_archival.txt',
                            main_dir + '/foo'}

        extract_dir = tmpdir.join('extract')
        tarf.extractall(path=extract_dir)

        metadata_lines = extract_dir.join(main_dir,
                                          '.hg_archival.txt').readlines()
        assert 'node: %s\n' % node in metadata_lines
        assert extract_dir.join(main_dir, 'foo').read() == 'archived'


def test_export_import(test_project, tmpdir):
    proj = test_project
    repo_path = tmpdir.join('repo1')

    repo = LocalRepo.clone(proj.owner_basic_auth_url, repo_path)
    repo_path.join('foo').write('foo0')
    repo.hg('commit', '-Am', "Commit 0")
    repo.hg('phase', '-p', ".")
    repo.hg('topic', 'zetop')
    repo_path.join('foo').write('foo1')
    repo.hg('commit', '-Am', "Commit 1")
    repo.hg('push')

    tarball = BytesIO()
    test_project.api_export(tarball, timeout_factor=3)

    tarball.seek(0)
    with Project.api_import_tarball(
            proj.heptapod,
            proj.owner,
            unique_name('test_import'),
            tarball,
    ) as imported:
        # in case the default vcs_type would be `hg_git` but the
        # test run would be for `hg` (native mode), this would fail:
        assert imported.vcs_type == test_project.vcs_type

        assert imported.api_branch_titles() == {
            'branch/default': 'Commit 0',
            'topic/default/zetop': 'Commit 1',
        }

        # being able to clone is a thing in itself
        clone = LocalRepo.clone(imported.owner_basic_auth_url,
                                tmpdir.join('import_clone'))

        # hg exchange commands exit with code 1 when there are no changes
        clone.hg('outgoing', repo_path, expected_return_code=1)
        clone.hg('incoming', repo_path, expected_return_code=1)

        # final check for phases
        log = clone.hg('log', '-T', '{desc}:{phase}:{topic}\n')
        assert log.splitlines() == ['Commit 1:draft:zetop',
                                    'Commit 0:public:',
                                    ]


@needs.hg_native
@needs.fs_access
def test_export_import_aux_git(test_project, tmpdir):
    proj = test_project
    repo_path = tmpdir.join('repo1')

    test_project.hg_git_repo_expected = True

    repo = LocalRepo.clone(proj.owner_basic_auth_url, repo_path)
    repo_path.join('foo').write('foo0')
    repo.hg('commit', '-Am', "Commit 0")
    repo.hg('phase', '-p', ".")
    repo.hg('topic', 'zetop')
    repo_path.join('foo').write('foo1')
    repo.hg('commit', '-Am', "Commit 1")
    repo.hg('push')

    git_repo = GitRepo(test_project.fs_path_git)
    expected_branches = {
        'branch/default': 'Commit 0',
        'topic/default/zetop': 'Commit 1',
    }
    # we need a mirror attempt to fill in the Git repo
    # using an URL that should actually work to avoid various cases of
    # not even starting the mirroring
    tgt_name = 'target_%s' % str(time.time()).replace('.', '_')
    owner = test_project.owner
    with Project.api_create(proj.heptapod, owner, tgt_name,
                            vcs_type='git') as git_tgt:
        mirror = test_project.api_create_mirror(
            url=git_tgt.owner_basic_auth_url,
            enabled=True,
            hg_mirror_type=None,
        )
        mirror.api_trigger()
        wait_assert(lambda: os.path.exists(git_repo.path),
                    lambda info: info)
        wait_assert(lambda: git_repo.branch_titles(),
                    lambda info: info == expected_branches)

    tarball = BytesIO()
    test_project.api_export(tarball, timeout_factor=3)

    tarball.seek(0)
    with Project.api_import_tarball(
            proj.heptapod,
            proj.owner,
            unique_name('test_import'),
            tarball,
    ) as imported:
        # in case the default vcs_type would be `hg_git` but the
        # test run would be for `hg` (native mode), this would fail:
        assert imported.vcs_type == test_project.vcs_type

        assert imported.api_branch_titles() == {
            'branch/default': 'Commit 0',
            'topic/default/zetop': 'Commit 1',
        }
        imported_git = GitRepo(imported.fs_path_git)
        assert imported_git.branch_titles() == expected_branches


def test_raw_blob(test_project, tmpdir):
    proj = test_project
    repo_path = tmpdir.join('repo1')

    repo = LocalRepo.clone(proj.owner_basic_auth_url, repo_path)
    repo_path.join('foo').write('foo0')
    repo.hg('commit', '-Am', "Commit 0")
    repo.hg('phase', '-p', ".")
    repo.hg('push')

    # using the Tree API makes this test work in the hg-git case
    # (not depending on internal knowledge about the blob oid), and
    # validates that our usage of the API works, which is a good hint
    # when debugging the two (R)HGitaly cases
    branches = proj.api_branches()
    assert list(branches.keys()) == ['branch/default']
    blob_oid = proj.api_get_tree()['foo']['oid']
    raw = proj.api_get_raw_blob(blob_oid)
    assert raw == 'foo0'


@needs.hg_native
def test_raw_diff_patch(test_project, tmpdir):
    proj = test_project
    repo_path = tmpdir.join('repo1')

    repo = LocalRepo.clone(proj.owner_basic_auth_url, repo_path)
    repo_path.join('foo').write('foo0')
    repo.hg('commit', '-Am', "Commit 0")
    repo.hg('phase', '-p', ".")
    node = repo.node('.')
    repo.hg('push')

    expected_line = '@@ -0,0 +1,1 @@\n+foo0'
    diff = test_project.webdriver_commit_raw(node, 'diff')
    assert diff.startswith('diff --git a/foo b/foo')
    assert expected_line in diff

    patch = test_project.webdriver_commit_raw(node, 'patch')
    assert patch.startswith('# HG changeset patch')
    assert expected_line in patch


def test_webdriver_project_settings(test_project):
    # MR settings
    proj = test_project
    proj.webdriver_update_merge_request_settings('ff')
    assert proj.api_get_field('merge_method') == 'ff'

    # CI/CD settings
    driver = proj.webdriver_get_settings_page('ci_cd')
    page = driver.page_source
    assert 'hg pull' in page
    assert 'hg clone' in page
    assert 'git fetch' not in page
    assert 'git clone' not in page

    # Mercurial settings


def test_vcs_type_stats(test_project):
    heptapod = test_project.heptapod
    resp = heptapod.api_get(subpath='projects/vcs_type_stats',
                            user=heptapod.users['root'])
    assert resp.status_code < 400
    stats = resp.json()

    # we cannot assert much more, given the previous history of the instance
    # In CI, we expect of course the value for the current VCS Type to be 1
    assert test_project.vcs_type in stats
    assert stats[test_project.vcs_type] > 0


def test_webdriver_roles(test_project):
    driver = test_project.owner_user.webdriver
    driver.get(test_project.url + '/-/project_members')
    wait_could_click_button(driver, data_testid='invite-members-button')
    # In HDK context, we need this extra temporization, otherwise we
    # get a Webpack error.
    wait_element_visible(driver, By.CSS_SELECTOR, 'h2.modal-title')
    wait_could_click(driver, By.XPATH,
                     '//*[@data-testid="access-level-dropdown"]')
    wait_could_click(driver, By.XPATH,
                     '//*[@data-testid="listbox-item-MERCURIAL_PUBLISHER"]')

    # at this point we are sure that Mercurial Publisher is offered
    # (see heptapod#1823), now let's try and use it.

    wait_could_click(driver, By.XPATH,
                     '//*[@data-testid="members-form-group"]')
    input_elt = driver.find_element(
        By.XPATH, '//input[@data-testid="members-token-select-input"]')
    input_elt.send_keys('test_basic')
    wait_could_click_button(driver, role='menuitem', type='button')

    wait_could_click_button(driver, data_testid='invite-modal-submit')

    # member information is not immediately available from API
    member = test_project.wait_assert_user_member(user_name='test_basic')
    assert member['access_level'] == ProjectAccess.HG_PUBLISHER
