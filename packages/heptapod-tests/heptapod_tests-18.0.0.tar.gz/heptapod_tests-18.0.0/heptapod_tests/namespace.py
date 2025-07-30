# Copyright 2019-2022 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 3 or any later version.
#
# SPDX-License-Identifier: GPL-3.0-or-later

from functools import cached_property

import attr
import requests

from selenium.webdriver.common.by import By

from .access_levels import GroupAccess
from .api import GitLabEntity
from .selenium import (
    wait_could_click,
    wait_could_click_button,
    webdriver_expand_settings,
)


class NameSpace(GitLabEntity):

    @property
    def url(self):
        return '/'.join((self.heptapod.url, self.full_path))

    def api_migrate_native(self, run_again=False, user=None, check=True):
        if user is None:
            user = self.owner_user

        # in subclasses, will not be under `self.api_url`
        resp = requests.post(
            f'{self.heptapod.url}/api/v4/namespaces/{self.id}'
            '/hg_migrate_native',
            headers={'Private-Token': user.token},
        )
        if not check:
            return resp

        assert resp.status_code < 400


@attr.s
class UserNameSpace(NameSpace):
    user_name = attr.ib()
    heptapod = attr.ib()

    @property
    def full_path(self):
        return self.user_name

    def __eq__(self, other):
        return other.__class__ == self.__class__ and self.user == other.user

    @cached_property
    def id(self):
        user = self.heptapod.get_user(self.user_name)
        resp = requests.get(self.heptapod.api_url + '/namespaces',
                            params=dict(owner_only=True),
                            headers=user.token_headers())
        assert resp.status_code == 200
        for ns in resp.json():
            if ns['kind'] == 'user':
                return ns['id']
        raise LookupError(
            "Personal namespace details for %r could not be found" % user)


@attr.s
class Group(NameSpace):

    id = attr.ib()
    path = attr.ib()
    full_path = attr.ib()
    heptapod = attr.ib()
    owner_name = attr.ib(default=None)

    api_uri = '/api/v4/groups'

    @classmethod
    def api_create(cls, heptapod, group_path,
                   user_name='root',
                   parent=None,
                   **data):
        data['name'] = data['path'] = group_path
        if parent is not None:
            data['parent_id'] = parent.id

        headers = {'Private-Token': heptapod.users[user_name].token}
        resp = requests.post(heptapod.url + cls.api_uri,
                             headers=headers,
                             data=data)
        assert resp.status_code == 201
        return cls.from_api_entity(heptapod, resp.json(), owner_name=user_name)

    def __eq__(self, other):
        return self.id == other.id

    @classmethod
    def api_retrieve(cls, heptapod, group_id, owner_name=None):
        """Return a checked Group object for the given id.

        :owner_name: if specified, registered as :attr:`owner_name` on the
           returned object, and used for all API calls, including the check
           performed by this method.
        """
        grp = Group(heptapod=heptapod,
                    id=group_id,
                    full_path=None,
                    owner_name=owner_name,
                    path=None)
        resp = grp.api_get()
        assert resp.status_code == 200
        info = resp.json()
        grp.path = info['path']
        grp.full_path = info['full_path']
        return grp

    @classmethod
    def from_api_entity(cls, heptapod, data, owner_name=None):
        """Construct a Group instance from data returned by the API."""
        return cls(heptapod=heptapod,
                   id=data['id'],
                   full_path=data['full_path'],
                   path=data['path'],
                   owner_name=owner_name,
                   )

    @classmethod
    def api_search(cls, heptapod, group_name, user_name='root',
                   owner_name=None):
        """Perform a search based on Group name and return workable instance.

        :param user_name: The user that performs the search
        :param owner_name: An owner, if known before hand.
        """
        headers = {'Private-Token': heptapod.users[user_name].token}
        resp = requests.get(heptapod.url + cls.api_uri,
                            headers=headers,
                            params=dict(search=group_name))
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        # TODO retrieve a suitable Owner if `owner_name` is None
        return cls.from_api_entity(heptapod, data[0], owner_name=owner_name)

    @property
    def owner_user(self):
        return self.heptapod.get_user(self.owner_name)

    @property
    def api_url(self):
        return self.heptapod.url + self.api_uri + '/%d' % self.id

    def settings_page_url(self, page='edit'):
        """Settings page URL.

        :param page: the path component to the wished page, e.g:
          - General: ``edit``
          - Integrations: ``settings/integrations``
          - CI/CD: ``settings/ci-cd``
          (etc)
        """
        return '/'.join((self.heptapod.url, 'groups', self.path, '-', page))

    def api_delete(self):
        resp = super(Group, self).api_delete()
        assert resp.status_code in (202, 204)

    def grant_member_access(self, user, level):
        """Grant given user the given access level.

        It doesn't matter whether the user is already a member or not: this
        method abstracts over it.

        This method is idempotent.

        TODO factorize with Project (as surely is done in the Rails app)
        """
        assert level in GroupAccess

        user_id = user.id
        resp = self.api_get(subpath='members/%d' % user_id)
        if resp.status_code == 404:
            subpath = 'members'
            meth = self.api_post
        else:
            subpath = 'members/%d' % user_id
            meth = self.api_put

        resp = meth(subpath=subpath, data=dict(user_id=user_id,
                                               access_level=int(level)))
        assert resp.status_code < 400

    def custom_attribute_api_url(self, key):
        return '/'.join((self.api_url, 'custom_attributes', key))

    def api_set_custom_attribute(self, key, value, user=None):
        if user is None:
            user = self.heptapod.get_user('root')

        resp = requests.put(self.custom_attribute_api_url(key),
                            headers={'Private-Token': user.token},
                            data=dict(value=value))

        assert resp.status_code == 200
        return resp.json()

    def api_get_custom_attribute(self, key, check=True, user=None):
        if user is None:
            user = self.heptapod.get_user('root')

        resp = requests.get(self.custom_attribute_api_url(key),
                            headers={'Private-Token': user.token})

        if not check:
            return resp

        assert resp.status_code < 400
        return resp.json()['value']

    def fs_path(self):
        return '/'.join((self.heptapod.repositories_root, self.full_path))

    def put_hgrc(self, lines):
        """Replace group's server-side HGRC with given lines.

        The lines have to include LF, same as with `writelines()`.
        """
        fs_path = self.fs_path()
        self.heptapod.run_shell(('mkdir', '-p', fs_path), user='git')
        self.heptapod.put_file_lines(fs_path + '/hgrc', lines)

    def webdriver_set_default_vcs_type(self, vcs_type):
        driver = self.heptapod.users[self.owner_name].webdriver

        driver.get(self.settings_page_url(page='settings/repository'))
        section_xpath = webdriver_expand_settings(driver,
                                                  'js-group-vcs-settings')
        wait_could_click(driver, By.XPATH,
                         section_xpath
                         + '//select[@id = "group_default_vcs_type"]'
                         + f'//option[@value = "{vcs_type}"]')
        wait_could_click_button(
            driver,
            data_qa_selector='vcs_save_changes_button',
        )

    def __enter__(self):
        return self

    def __exit__(self, *exc_args):
        self.api_delete()
        return False
