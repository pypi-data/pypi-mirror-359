import pytest
from . import needs

from heptapod_tests.access_levels import GroupAccess
from heptapod_tests.namespace import Group
from heptapod_tests.project import Project
from heptapod_tests.user import User
from heptapod_tests.utils import (
    unique_name,
)

from .test_push import prepare_simple_repo

parametrize = pytest.mark.parametrize


@needs.fs_access
def test_group_project(heptapod):
    inner_test_group_project(heptapod, hashed_storage=True)


@needs.services
@needs.docker
def test_group_project_legacy_storage(heptapod):
    inner_test_group_project(heptapod, hashed_storage=False)


def inner_test_group_project(heptapod, hashed_storage):
    group = group2 = None
    group_name = unique_name('test_group')
    group2_name = unique_name('transfer_target')
    try:
        group = Group.api_create(heptapod, group_name, user_name='test_basic')
        assert group.path == group_name
        assert group.full_path == group_name
        found = Group.api_search(heptapod, group_name, owner_name='test_basic')
        assert found == group

        # we can be more confident with group2
        group2 = Group.api_create(heptapod, group2_name,
                                  user_name='test_basic')
        project = Project.api_create(heptapod,
                                     project_name='test_proj',
                                     user_name='test_basic',
                                     group=group)
        assert project.api_get_field('path_with_namespace') == '/'.join(
            (group_name, 'test_proj'))
        if not hashed_storage:
            project.make_storage_legacy()

        group.put_hgrc(("[experimental]\n",
                        "groupconf=test\n"))
        group2.put_hgrc(("[experimental]\n",
                         "groupconf=transferred\n"))
        assert project.hg_config('experimental')['groupconf'] == 'test'

        # hgrc PUT does not affect inheritance by default
        resp = project.api_hgrc_set(allow_bookmarks=True)
        assert resp.status_code == 204
        assert project.hg_config('experimental')['groupconf'] == 'test'

        # now let's turn inheritance off
        resp = project.api_hgrc_set(inherit=False)
        assert resp.status_code == 204
        assert 'groupconf' not in project.hg_config('experimental')

        # and finally, let's turn inheritance back on
        resp = project.api_hgrc_set(inherit=True)
        assert resp.status_code == 204
        assert project.hg_config('experimental')['groupconf'] == 'test'

        # time to transfer to group2 and check inheritance does it magic
        resp = project.api_transfer(group2)
        assert resp.status_code < 400
        assert project.hg_config('experimental')['groupconf'] == 'transferred'
    finally:
        if group is not None:
            group.api_delete()


def test_group_project_push(heptapod, tmpdir):
    with Group.api_create(heptapod, unique_name('test_group'),
                          user_name='test_basic') as group:
        with Project.api_create(heptapod,
                                project_name='test_proj',
                                user_name='test_basic',
                                group=group) as project:
            prepare_simple_repo(project, tmpdir / 'repo')
            assert project.api_branch_titles() == {
                'branch/default': 'Commit 0',
                'topic/default/zetop': 'Commit 1',
            }


def test_custom_attributes_perms(heptapod):
    """Ensuring that these are as private as we think they are."""
    owner = heptapod.get_user('test_basic')
    admin = heptapod.get_user('root')
    with Group.api_create(heptapod, unique_name('test_group'),
                          user_name=owner.name) as group:
        # first check that custom attributes do work
        group.api_set_custom_attribute('location', 'secret lair',
                                       user=admin)
        assert group.api_get_custom_attribute('location',
                                              user=admin) == 'secret lair'

        def assert_forbidden(user):
            resp = group.api_get_custom_attribute('location', user=user,
                                                  check=False)
            assert resp.status_code == 403

        with User.create(heptapod,
                         unique_name('user_custom_attr')) as user:
            for level in GroupAccess:
                group.grant_member_access(user, level)
                # Even OWNER is forbidden. If that were to
                # change it probably wouldn't be really shocking.
                assert_forbidden(owner)


def test_webdriver_vcs_types(test_group):
    info = test_group.api_get().json()
    assert info['default_vcs_type'] == 'hg'
    test_group.webdriver_set_default_vcs_type('git')

    info = test_group.api_get().json()
    assert info['default_vcs_type'] == 'git'


@needs.fs_access
def test_subgroups(heptapod):
    inner_test_subgroups(heptapod, hashed_storage=True)


@needs.docker
@needs.services
def test_subgroups_legacy_storage(heptapod):
    inner_test_subgroups(heptapod, hashed_storage=False)


def inner_test_subgroups(heptapod, hashed_storage):
    user_name = 'test_basic'
    group = subgroup = None
    group_name = unique_name('test_group')
    try:
        group = Group.api_create(heptapod, group_name,
                                 user_name=user_name)
        subgroup = Group.api_create(heptapod, 'sub',
                                    parent=group,
                                    user_name=user_name)
        assert subgroup.full_path == group_name + '/sub'
        project = Project.api_create(heptapod,
                                     project_name='proj',
                                     user_name='test_basic',
                                     group=subgroup)
        assert project.api_get_field(
            'path_with_namespace') == group_name + '/sub/proj'

        if not hashed_storage:
            project.make_storage_legacy()

        # enclosing group HGRC is propagated
        group.put_hgrc(("[experimental]\n",
                        "groupconf=test\n"))
        assert project.hg_config('experimental')['groupconf'] == 'test'

        # note: this shadows inclusion of the enclosing group HGRC
        # but that doesn't matter for this test
        subgroup.put_hgrc(("[experimental]\n",
                           "subgroup=yes\n"))
        assert project.hg_config('experimental')['subgroup'] == 'yes'

        # a new project creation does *not* reset the subgroup hgrc
        proj2 = Project.api_create(heptapod,
                                   project_name='proj2',
                                   user_name='test_basic',
                                   group=subgroup)
        assert project.hg_config('experimental')['subgroup'] == 'yes'
        # that to fail would be really surprising:
        assert proj2.hg_config('experimental')['subgroup'] == 'yes'
    finally:
        if subgroup is not None:
            subgroup.api_delete()
        if group is not None:
            group.api_delete()
