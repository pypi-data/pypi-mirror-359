# Copyright 2020 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 3 or any later version.
#
# SPDX-License-Identifier: GPL-3.0-or-later

import attr
from urllib.parse import urlparse

from selenium.webdriver.common.by import By

from .selenium import (
    wait_could_click,
    webdriver_expand_settings,
)
from .ssh import (
    url_server_keys,
)


@attr.s
class ProjectMirror:
    id = attr.ib()
    project = attr.ib()

    @classmethod
    def api_create(cls, project, **data):
        url = urlparse(data['url'])
        if url.scheme == 'ssh' and 'ssh_known_hosts' not in data:
            data['ssh_known_hosts'] = url_server_keys(url)
        resp = project.api_post(subpath='remote_mirrors',
                                data=data)

        assert resp.status_code < 300
        if data.get('hg_mirror_type') is None:  # mirroring to Git
            project.hg_git_repo_expected = True

        return cls(project=project, id=resp.json()['id'])

    @classmethod
    def api_list(cls, project, user=None, check=True):
        """Return a list of dicts, not of ProjectMirror instances.

        The reason is that ProjectMirror currently does not keep more
        state than that's needed for identification.
        """
        resp = project.api_get(subpath='remote_mirrors', user=user)
        if not check:
            return resp
        assert resp.status_code < 300
        return resp.json()

    @property
    def api_subpath(self):
        return 'remote_mirrors/%d' % self.id

    def api_update(self, check=True, **data):
        resp = self.project.api_put(subpath=self.api_subpath, **data)

        if not check:
            return resp

        assert resp.status_code < 300
        return resp.json()

    def api_get(self):
        # no direct method for that, have to resort to the list
        for info in self.api_list(self.project):
            if info['id'] == self.id:
                return info
        raise LookupError(self)

    def api_trigger(self, check=True):
        resp = self.project.api_put(
            subpath=self.api_subpath + '/trigger')
        if not check:
            return resp

        assert resp.status_code < 300

    def webdriver_trigger(self):
        proj = self.project
        driver = proj.owner_webdriver
        driver.get(proj.url + '/-/settings/repository')
        webdriver_expand_settings(driver, 'js-push-remote-settings')
        wait_could_click(driver, By.XPATH,
                         '//a[@data-testid="update-now-button"]')

    def webdriver_ssh_pub_key(self):
        proj = self.project
        driver = proj.owner_webdriver
        driver.get(proj.url + '/-/settings/repository')
        webdriver_expand_settings(driver, 'js-push-remote-settings')
        btn = driver.find_element(
            By.XPATH, '//button[@data-testid="copy-public-key-button"]')
        return btn.get_attribute('data-clipboard-text')
