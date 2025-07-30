# Copyright 2020 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
import pytest

from heptapod_tests.content import prepare_import_source_hg
from heptapod_tests.git import LocalRepo as GitRepo
from heptapod_tests.hg import LocalRepo, assert_matching_changesets
from . import needs

parametrize = pytest.mark.parametrize


def test_create(test_project):
    url = 'https://hg.test'
    mirror = test_project.api_create_mirror(url=url,
                                            hg_mirror_type='hg-pull')

    info = mirror.api_get()
    assert info['url'] == url
    assert info['hg_mirror_type'] == 'hg-pull'
    assert info['enabled'] is False


def test_update(test_project):
    url = 'https://hg.test'
    mirror = test_project.api_create_mirror(url=url,
                                            hg_mirror_type='hg-pull')

    info = mirror.api_update(
        data={"url": "https://other.test", "enabled": True})
    assert info['url'] == url  # Gitlab does not allow updating the url
    assert info['enabled'] is True


@parametrize('trigger', ('api', 'webdriver'))
def test_pull(test_project, public_project, tmpdir, trigger):
    """Test hg-pull mirror"""

    src_repo, src_url = prepare_import_source_hg(public_project, tmpdir,
                                                 tweak_hgrc=False)
    print("Graph of source project after push:")
    print(src_repo.graphlog())
    print("Url of the mirror target")
    print(src_url)

    mirror = test_project.api_create_mirror(url=src_url,
                                            enabled=True,
                                            hg_mirror_type='hg-pull')

    if trigger == 'webdriver':
        mirror.webdriver_trigger()
    else:
        res = mirror.api_trigger(check=False)
        assert res.status_code == 204

    # Check that Gitlab became aware of the changes done by the pull
    test_project.wait_assert_api_branches(
        lambda branches: "topic/default/antelope" in branches,
        timeout_factor=3,
    )

    clone = LocalRepo.clone(test_project.owner_basic_auth_url,
                            tmpdir.join('target-repo'))
    assert_matching_changesets(clone, src_repo, ('node', 'desc'))


def test_push_http(test_project, public_project, tmpdir):
    """Test hg-push HTTP mirror"""

    src_repo, _ = prepare_import_source_hg(test_project, tmpdir,
                                           tweak_hgrc=False)
    print("Graph of source project after push:")
    print(src_repo.graphlog())

    mirror = test_project.api_create_mirror(
        url=public_project.owner_basic_auth_url,
        enabled=True,
        hg_mirror_type='hg-push')

    # the mirror is also triggered at creation, but we should not get errors
    # in the manual triggering
    res = mirror.api_trigger(check=False)
    assert res.status_code == 204

    # Check that Gitlab became aware of the changes done by the pull
    # note that `include_drafts` is not exposed on the Rails side,
    # hence the default `false` value applies.
    public_project.wait_assert_api_branches(
        lambda branches: "branch/default" in branches,
        empty_on_error=True,
        timeout_factor=3,
    )

    clone = LocalRepo.clone(public_project.owner_basic_auth_url,
                            tmpdir.join('target-repo'))
    assert_matching_changesets(clone, src_repo, ('node', 'desc'),
                               revs='public()')


@parametrize('bookmarks', ('with', 'without'))
def test_pull_bookmarks(test_project, public_project, tmpdir, bookmarks):
    """Test hg-pull mirror"""
    with_bookmarks = bookmarks == 'with'
    if with_bookmarks:
        test_project.api_hgrc_set(inherit=True, allow_bookmarks=True)

    src_repo, src_url = prepare_import_source_hg(public_project, tmpdir,
                                                 tweak_hgrc=False)
    public_project.api_hgrc_set(inherit=True, allow_bookmarks=True)
    src_repo.hg('bookmark', '-r', '0', 'book1')
    src_repo.hg('push', '-B', 'book1', expected_return_code=1)
    print("Graph of source project after push:")
    print(src_repo.graphlog())
    print("Url of the mirror target")
    print(src_url)

    mirror = test_project.api_create_mirror(url=src_url,
                                            enabled=True,
                                            hg_mirror_type='hg-pull')

    res = mirror.api_trigger(check=False)
    assert res.status_code == 204

    # Check that Gitlab became aware of the changes done by the pull
    test_project.wait_assert_api_branches(
        lambda branches: "topic/default/antelope" in branches,
        timeout_factor=3,
    )

    assert ('book1' in test_project.api_branches()) is with_bookmarks

    clone = LocalRepo.clone(test_project.owner_basic_auth_url,
                            tmpdir.join('target-repo'))
    fields = ['node', 'desc']
    if with_bookmarks:
        fields.append('bookmarks')
    else:
        assert 'no bookmarks' in clone.hg('bookmarks')

    assert_matching_changesets(clone, src_repo, fields)


@needs.hg_native
@parametrize('protocol', ('http', 'ssh'))
@parametrize('trigger', ('push', 'manual'))
def test_push_to_git(test_project, git_project, tmpdir, protocol, trigger):
    """Test hg-push HTTP mirror"""

    if trigger == 'manual':
        src_repo, _ = prepare_import_source_hg(test_project, tmpdir,
                                               tweak_hgrc=False)

    attrs = dict(enabled=True, hg_mirror_type=None)
    if protocol == 'http':
        url = git_project.owner_basic_auth_url + '.git/'
    else:
        url = git_project.owner_ssh_params[1]
        attrs['auth_method'] = 'ssh_public_key'

    mirror = test_project.api_create_mirror(url=url, **attrs)

    if protocol == 'ssh':
        ssh_pub_key = mirror.webdriver_ssh_pub_key()
        git_project.api_add_deploy_key(ssh_pub_key, can_push=True)

    if trigger == 'push':
        # mirrors have a temporisation to avoid running in fast succession
        # (see `BACKOFF_DELAY` in `app/models/remote_mirror.rb`), hence we
        # have to rely on this parametrization to test both kinds of triggering
        src_repo, _ = prepare_import_source_hg(test_project, tmpdir,
                                               tweak_hgrc=False)
    else:
        res = mirror.api_trigger(check=False)
        assert res.status_code == 204

    # Check that Gitlab became aware of the changes done by the push
    git_project.wait_assert_api_branches(
        lambda branches: "topic/default/antelope" in branches,
        timeout_factor=3,
    )
    assert git_project.api_branch_titles() == {
        'branch/default': 'Even a horse!',
        'topic/default/antelope': 'Même une antilope !'
    }
    clone = GitRepo.clone(git_project.owner_basic_auth_url,
                          tmpdir.join('target-repo'))
    assert set(clone.git('log', '--all', '--format=%s').splitlines()) == {
        'Même une antilope !',
        'Even a horse!',
        'Initial sentence',
    }
