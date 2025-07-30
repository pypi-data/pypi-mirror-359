import pytest
import requests
from subprocess import CalledProcessError

from heptapod_tests.access_levels import GroupAccess
from heptapod_tests.hg import (
    LocalRepo,
)
from heptapod_tests.namespace import Group
from heptapod_tests.project import Project
from heptapod_tests.utils import unique_name

from . import needs


parametrize = pytest.mark.parametrize


@pytest.fixture
def pub_project_in_group(heptapod):
    test_basic = heptapod.users['test_basic']
    with Group.api_create(heptapod, unique_name('test_group'),
                          visibility='public',
                          user_name='root') as group:
        group.grant_member_access(test_basic, GroupAccess.OWNER)
        with Project.api_create(heptapod, 'test_basic', 'with-clonebundles',
                                visibility='public',
                                group=group) as proj:
            yield proj


def prepare_simple_repo(proj, repo_path):
    repo = LocalRepo.init(repo_path, default_url=proj.owner_basic_auth_url)

    repo_path.join('foo').write('foo0')
    repo.hg('commit', '-Am', "Commit 0")
    repo.hg('phase', '-p', ".")
    repo.hg('topic', 'zetop')

    repo_path.join('foo').write('foo1')
    repo.hg('commit', '-Am', "Commit 1")
    return repo


@needs.fs_access
@needs.hg_native  # hg_git not supported although it *might* work by accident
@parametrize('trigger', ('api-refresh', 'on-change-http', 'on-change-ssh'))
def test_public_clone_bundles(pub_project_in_group, tmpdir, trigger):
    proj = pub_project_in_group
    on_change = trigger.startswith('on-change')

    proj.extend_hgrc('[clone-bundles]', 'trigger.below-bundled-ratio=1.0')
    proj.api_hgrc_set(clone_bundles='on-change' if on_change else 'explicit')

    repo = prepare_simple_repo(proj, tmpdir.join('repo1'))

    if trigger == 'on-change-ssh':
        ssh_cmd, ssh_url = proj.owner_ssh_params
        repo.hg('push', '--ssh', ssh_cmd, ssh_url)
    else:
        repo.hg('push', proj.owner_basic_auth_url)

    if not on_change:
        proj.api_refresh_clone_bundles()
    bundles = proj.wait_assert_clone_bundles_autogen(
        lambda bundle: bundle['state'] == 'DONE',
        timeout_factor=3,
    )
    bundle = bundles[0]
    assert bundle['node'] == repo.node('0')  # public changeset
    bundle_url = bundle['url']
    assert requests.head(bundle_url).status_code == 200

    # not using LocalRepo.clone() because we want to assert on stdout
    clone = LocalRepo.init(tmpdir.join('clone'), default_url=proj.url)
    out = clone.hg('pull')
    assert f'applying clone bundle from {bundle_url}' in out

    Extract, extracts = clone.changeset_extracts(('desc', 'phase', 'topic'))
    assert extracts == (
        Extract(desc='Commit 1', phase='draft', topic='zetop'),
        Extract(desc='Commit 0', phase='public', topic=''),
    )


@needs.fs_access
@needs.hg_native  # hg_git not supported although it *might* work by accident
@parametrize('trigger', ('api-refresh', 'on-change-http', 'on-change-ssh'))
def test_private_clone_bundles(test_project, tmpdir, trigger):
    proj = test_project
    on_change = trigger.startswith('on-change')

    proj.extend_hgrc('[clone-bundles]', 'trigger.below-bundled-ratio=1.0')
    proj.api_hgrc_set(clone_bundles='on-change' if on_change else 'explicit')

    repo = prepare_simple_repo(proj, tmpdir.join('repo1'))

    if trigger == 'on-change-ssh':
        ssh_cmd, ssh_url = proj.owner_ssh_params
        repo.hg('push', '--ssh', ssh_cmd, ssh_url)
    else:
        repo.hg('push', proj.owner_basic_auth_url)

    if not on_change:
        proj.api_refresh_clone_bundles()
    bundles = proj.wait_assert_clone_bundles_autogen(
        lambda bundle: bundle['state'] == 'DONE',
        timeout_factor=3,
    )
    bundle = bundles[0]
    assert bundle['node'] == repo.node('0')  # public changeset

    # not using LocalRepo.clone() because we want to assert on stdout
    clone = LocalRepo.init(tmpdir.join('clone'),
                           default_url=proj.owner_basic_auth_url)
    out = clone.hg('pull')
    assert 'applying clone bundle from ' in out

    Extract, extracts = clone.changeset_extracts(('desc', 'phase', 'topic'))
    assert extracts == (
        Extract(desc='Commit 1', phase='draft', topic='zetop'),
        Extract(desc='Commit 0', phase='public', topic=''),
    )

    # anonymous access fails
    with pytest.raises(CalledProcessError):
        LocalRepo.clone(proj.url, tmpdir / 'anon-clone')

    # authenticated non-member access fails
    with pytest.raises(CalledProcessError):
        LocalRepo.clone(proj.basic_auth_url('test_basic'),
                        tmpdir / 'non-member-clone')


@needs.fs_access
@needs.hg_native  # hg_git not supported although it *might* work by accident
def test_clone_bundles_gc(pub_project_in_group, tmpdir):
    proj = pub_project_in_group
    proj.extend_hgrc('[clone-bundles]', 'trigger.below-bundled-ratio=1.0')
    proj.api_hgrc_set(clone_bundles='explicit')

    repo = prepare_simple_repo(proj, tmpdir.join('repo1'))
    proj.api_hgrc_set(clone_bundles='on-change')
    repo.hg('push', proj.owner_basic_auth_url)

    bundles = proj.wait_assert_clone_bundles_autogen(
        lambda bundle: bundle['state'] == 'DONE',
        timeout_factor=3,
    )
    first_bundle = bundles[0]
    node0 = repo.node('0')
    assert first_bundle['node'] == node0

    repo.hg('up', 'default')
    for i in range(2, 4):
        repo.path.join('foo').write(f'foo{i}')
        repo.hg('commit', '-Am', f"Commit {i}")
        repo.hg('phase', '-pr', '.')  # just to avoid red herrings
        repo.hg('push', proj.owner_basic_auth_url)

        bundles = proj.wait_assert_clone_bundles_autogen(
            lambda bundle: (bundle['state'] == 'DONE'
                            and bundle['node'] == repo.node(str(i))),
            index=-1,
            timeout_factor=3,
        )

    # the first bundle is no longer in manifest
    assert len(bundles) < 3
    assert not any(b['node'] == node0 for b in bundles)

    # the first bundle was removed from storage
    # (considering an HTTP 404 to be proof enough)
    assert requests.head(first_bundle['url']).status_code in (403, 404)
