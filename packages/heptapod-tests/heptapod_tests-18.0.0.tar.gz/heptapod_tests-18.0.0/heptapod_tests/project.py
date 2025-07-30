# Copyright 2018 Paul Morelle <madprog@htkc.org>
# Copyright 2019-2022 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 3 or any later version.
#
# SPDX-License-Identifier: GPL-3.0-or-later

import attr
from base64 import b64decode
import hashlib
from io import BytesIO
import logging
import os
from pathlib import Path
import py
import re
import requests
from urllib.parse import (
    parse_qs,
    quote as urlquote,
    unquote as urlunquote,
    urlparse,
)
import time
import warnings

from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    StaleElementReferenceException
)
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from .access_levels import ProjectAccess
from .api import (
    api_request,
    GitLabEntity,
)
from .hg import LocalRepo
from .namespace import UserNameSpace
from .merge_request import MergeRequest
from .project_mirror import ProjectMirror
from .selenium import (
    could_click_element,
    raw_page_content,
    wait_assert_in_page_source,
    wait_could_click,
    wait_could_click_button,
    wait_could_click_element,
    wait_element_displayed,
    wait_element_visible,
    webdriver_expand_settings,
    webdriver_wait,
)
from .wait import (
    BASE_TIMEOUT,
    wait_assert,
)

logger = logging.getLogger(__name__)


def extract_gitlab_branch_titles(branches):
    return {name: info['commit']['title']
            for name, info in branches.items()}


def branch_title(all_branches, branch_name):
    """Return the title of head commit for the branch with given name.

    If no branch has the given name, ``None`` is returned.
    This is useful for one-liners (lambda) in ``wait_assert`` methods.
    """
    branch = all_branches.get(branch_name)
    if branch is None:
        return None

    return branch['commit']['title']


def protected_branch_api_subpath(spec=None):
    path = ['protected_branches']
    if spec is not None:
        path.append(urlquote(spec, safe=''))
    return '/'.join(path)


@attr.s
class Project(GitLabEntity):
    heptapod = attr.ib()
    name = attr.ib()
    group = attr.ib()
    # owner=None or id=None means it's not known yet, this should happen only
    # in the present module functions
    owner = attr.ib(default=None)
    id = attr.ib(default=None)
    # If vcs_type is None, this means Mercurial.
    # These functional tests should only exceptionally make a difference
    # between various ways Mercurial is supported ('hg_git', 'hgitaly'), and
    # preferably for temporary workarounds.
    vcs_type = attr.ib(default=None)
    is_legacy = attr.ib(default=False)
    hg_git_repo_expected = attr.ib(default=False)
    """For Mercurial, express whether an auxiliary Git repo is expected.

    This can be ``True`` in two cases:

    - because of general testing options. As of this writing, if
      ``--heptapod-hg-native`` is not set to ``without-git``.
    - because the Git repository is a functionally desireable outcome
      (see heptapod#125). In this case, the tests are expected to override
      the value, because it is initialized from the general testing options.
    """

    def owner_get(self, **kwargs):
        """A shortcut to perform a simple GET, with BasicAuth as the owner.

        All `kwargs` are passed directly to `requests.get()`
        """
        return requests.get(self.url, auth=self.owner_credentials, **kwargs)

    def get_session_cookie(self, webdriver):
        for cookie in webdriver.get_cookies():
            if cookie['name'].startswith('_gitlab_session'):
                return cookie
        raise LookupError("Could not find GitLab session cookie")

    def session_api_get(self, webdriver, subpath='', **kwargs):
        """Perform a simple GET, with the session cookie found in webdriver.

        The full URL is made of the API URL of the project, together with
        the given subpath (example '/merge_requests/1')
        """
        cookie = self.get_session_cookie(webdriver)
        return requests.get(
            '/'.join((self.api_url, subpath)),
            cookies={cookie['name']: cookie['value']})

    def api_edit(self, **params):
        """Perform a project API edit."""
        return api_request('PUT', self, self.owner_user, data=params)

    @property
    def owner_user(self):
        return self.heptapod.get_user(self.owner)

    def api_hgrc_set(self, user=None, **values):
        return self.user_api_request('PUT', user=user,
                                     subpath='hgrc', data=values)

    def owner_api_hgrc_get(self):
        return self.api_get(subpath='hgrc')

    def owner_api_hgrc_reset(self):
        return self.api_delete(subpath='hgrc')

    def owner_api_hg_heptapod_config(self):
        return self.api_get(subpath='hg_heptapod_config')

    def api_request(self, method, user, subpath='', **kwargs):
        """Perform a simple API HTTP request as the given user.

        `method` is the HTTP method to use, same as in `requests.request`.

        The full URL is made of the API URL of the project, together with
        the given subpath (example 'merge_requests/1').

        Appropriate authentication headers are added on the fly.

        All kwargs are passed to `requests.request()`
        """
        warnings.warn("Project.api_request() is deprecated. "
                      "Use user_api_request() instead.",
                      DeprecationWarning, stacklevel=2)
        return self.user_api_request(method, user=user, subpath=subpath,
                                     **kwargs)

    def api_get_field(self, key):
        """Return the value of a field by performing an API GET request.

        The request is made with full owner credentials.
        """
        resp = self.api_get()
        assert resp.status_code < 400
        return resp.json().get(key)

    def graphql_get_fields(self, fields, user=None, check=True):
        query = 'query {project(fullPath: "%s") {%s}}' % (
            self.full_path,
            ' '.join(fields)
        )
        if user is None:
            user = self.owner_user
        resp = user.graphql(query, check=check)
        if not check:
            return resp

        return resp['project']

    def api_get_info(self):
        """Return the full project information from API.

        The request is made with full owner credentials.
        """
        resp = self.api_get()
        assert resp.status_code < 400
        return resp.json()

    def api_get_commit_metadata(self, gl_sha, check=True):
        """Retrieve commit metadata with the API.

        :param gl_sha: the primary identifier of the commit from
           GitLab's point of view, hence a Git SHA if VCS type is `hg_git`.

        - does not have file content nor any diff
        - works with obsolete commits, unless garbage collected.
        """
        resp = self.api_get(subpath='repository/commits/' + gl_sha)
        if not check:
            return resp

        assert resp.status_code == 200
        return resp.json()

    @property
    def hg_native(self):
        # TODO simple placeholder for now. Later on we can
        # set it at creation / search time
        return self.heptapod.hg_native

    @property
    def owner_credentials(self):
        """Return (user, password)."""
        user = self.owner_user
        return user.name, user.password

    @property
    def owner_token(self):
        return self.owner_user.token

    @property
    def owner_webdriver(self):
        return self.owner_user.webdriver

    @property
    def relative_uri(self):
        return '/'.join((self.group.full_path, self.name))

    @property
    def url(self):
        return '/'.join((self.heptapod.url, self.relative_uri))

    @property
    def owner_ssh_params(self):
        """See `ssh_params()`
        """
        return self.ssh_params(self.owner)

    def ssh_params(self, user_name):
        """Provide command and URL to perform SSH operations as `user_name`
        Example::

           ('ssh -i /tmp/id_rsa', 'git@localhost:root/test_project.hg')

        """
        heptapod = self.heptapod
        ext = '.git' if self.vcs_type == 'git' else '.hg'
        url = '/'.join((heptapod.ssh_url, self.relative_uri + ext))
        return self.heptapod.get_user(user_name).ssh_command, url

    def git_ssh_params(self, user_name):
        """Similar to ssh_params, tailored for Git.
        """
        heptapod = self.heptapod
        cmd = self.ssh_params(user_name)[0] + ' -p %d' % heptapod.ssh_port
        address = '{heptapod.ssh_user}@{heptapod.host}:{path}'.format(
            heptapod=heptapod,
            path=self.relative_uri + '.git',
        )
        return cmd, address

    def basic_auth_url(self, user_name, pwd=None):
        """Produce an URL suitable for basic authentication, hence hg CLI.

        :param pwd: if not supplied, will be read from the permanent users
                    known of :attr:`heptapod`
        """
        heptapod = self.heptapod
        if pwd is None:
            user = self.heptapod.get_user(user_name)
            pwd = user.token if user.vcs_token_only else user.password
        url = heptapod.parsed_url
        return "{scheme}://{auth}@{netloc}/{path}".format(
            scheme=url.scheme,
            netloc=url.netloc,
            auth=':'.join((user_name, pwd)),
            path=self.relative_uri,
        )

    @property
    def owner_basic_auth_url(self):
        return self.basic_auth_url(self.owner)

    def deploy_token_url(self, token):
        return self.basic_auth_url(token['username'], pwd=token['token'])

    @property
    def api_url(self):
        return '/'.join((
            self.heptapod.url,
            'api', 'v4', 'projects',
            self.full_path.replace('/', '%2F')
        ))

    @property
    def full_path(self):
        return '/'.join((self.group.full_path, self.name))

    @property
    def fs_common_path(self):
        """Common abspath on Heptapod server FS (not ending with .hg nor .git)

        Meaningful only for those tests that require file system access.
        Relies on knowledge of internal GitLab details that may well change.
        (since these are tests, we would notice quickly).
        """
        disk_path = getattr(self, '_disk_path', None)
        if disk_path is not None:
            return disk_path

        if not self.is_legacy:
            sha2 = hashlib.sha256(b'%d' % self.id).hexdigest()
            rpath = '@hashed/%s/%s/%s' % (sha2[:2], sha2[2:4], sha2)
            disk_path = os.path.join(self.heptapod.repositories_root, rpath)
        else:
            disk_path = '/'.join((self.heptapod.repositories_root,
                                  self.group.full_path, self.name))
        self._disk_path = disk_path
        return disk_path

    @property
    def fs_path(self):
        """Path to the Mercurial repo on Heptapod server file system."""
        return self.fs_common_path + '.hg'

    @property
    def fs_path_git(self):
        """Path to the Git repo on Heptapod server file system.

        On native Mercurial projects, such a Git repository must be related
        to mirrors (strictly equivalent as of Heptapod 17.7.1)
        """
        git_path = self.fs_path_git_legacy()
        if self.vcs_type == 'hg_git':
            return git_path

        return git_path.replace('@hashed', '+hgitaly/hg-git/@hashed')

    def fs_path_git_legacy(self):
        return self.fs_common_path + '.git'

    def _change_storage(self, legacy):
        label = 'legacy' if legacy else 'hashed'
        if legacy is self.is_legacy:
            logger.warn("_change_storage: project %d is already on %s storage",
                        self.id, label)
        rake_cmd = 'rollback_to_legacy' if legacy else 'migrate_to_hashed'
        self.heptapod.rake('gitlab:storage:' + rake_cmd,
                           'ID_FROM=%d' % self.id,
                           'ID_TO=%d' % self.id)
        self.is_legacy = legacy
        self._disk_path = None

        # we're not inconsistent
        assert ('@hashed' in self.fs_path) is (not legacy)

        wait_assert(
            lambda: self.heptapod.execute(('test', '-e', self.fs_path))[0],
            lambda code: code == 0,
            timeout_factor=12,
            msg="Repository %r not found in %s storage" % (self.fs_path, label)
        )

    def make_storage_legacy(self):
        self._change_storage(True)

    def make_storage_hashed(self):
        self._change_storage(False)

    def rake_migrate_native(self):
        self.heptapod.rake(
            f'heptapod:experimental:hg_migrate_native'
            f'[{self.id},true,{self.owner_user.name}]'
        )

    def api_refresh_clone_bundles(self, check=True, user=None):
        if user is None:
            user = self.owner_user

        resp = api_request(
            'PUT', self, user, subpath='repository/hg_clone_bundles_refresh'
        )
        if not check:
            return resp

        assert resp.status_code == 204

    def read_clone_bundles_autogen(self):
        # at some point we might want to depend on the mercurial package
        # itself, but this will lead to potential problems (or just doubt) of
        # confusion with the client that is also in use.
        path = Path(self.fs_path) / '.hg/clonebundles.auto-gen'
        bundles = []
        try:
            with open(path) as fobj:
                for line in fobj:
                    line = line.split()
                    bundles.append(dict(state=line[0].split('-', 1)[0],
                                        node=line[4],
                                        url=urlunquote(line[5]),
                                        ))
        except FileNotFoundError:
            pass

        return bundles

    def wait_assert_clone_bundles_autogen(self, until, index=0, **wait_kw):
        def condition(bundles):
            try:
                bundle = bundles[index]
            except IndexError:
                return False
            return until(bundle)

        return wait_assert(lambda: self.read_clone_bundles_autogen(),
                           condition, **wait_kw)

    def api_migrate_native(self, run_again=False, user=None, check=True,
                           min_completion_time_factor=0):
        if user is None:
            user = self.owner_user

        min_comp_time = BASE_TIMEOUT * min_completion_time_factor
        resp = api_request(
            'POST', self, user, subpath='hg_migrate_native',
            data=dict(run_again=run_again,
                      testing_minimal_completion_time_seconds=min_comp_time
                      )
        )
        if not check:
            return resp

        assert resp.status_code < 400

    def webdriver_migrate_native(self, user=None):
        if user is None:
            user = self.owner_user

        driver = user.webdriver
        self.webdriver_mercurial_settings(driver)
        wait_could_click(
            driver, By.XPATH,
            '//a[@data-testid="migrate-native-project-link"]'
        )

        wait_could_click_button(
            driver,
            type='button',
            data_testid='confirm-ok-button'
        )

    def wait_assert_api_migrate_native(self, **kwargs):
        """Compatibility alias."""
        return self.wait_assert_migrate_native(method='api')

    def wait_assert_migrate_native(self, method='api', check_banner=False,
                                   **kwargs):
        """Migrate to native through API and wait_assert for completion.

        We wait first for the change of VCS type to native, then for
        unarchival, because waiting for the project archival would be at
        risk to miss the whole process if it turns out to be real fast.

        Chances are high that the project is unarchived very soon after
        the change of VCS type, but that does not matter.

        This process is unreliable if this is a rerun, as the VCS type and
        archival status are exactly as expected at the end from the onset.
        Hence it is possible, if the test is much faster than the server that
        the wait returns before the process even starts.

        Run-again tests expecting a visible change should wait_assert this
        precise change for better reliability.
        """
        if method == 'api':
            self.api_migrate_native(**kwargs)
        elif method == 'webdriver':
            self.webdriver_migrate_native(**kwargs)
        completion_factor = kwargs.get('min_completion_time_factor', 0)
        if check_banner:
            driver = self.owner_webdriver
            driver.get(self.url)
            wait_element_visible(driver, By.XPATH,
                                 '//*[@data-testid="hg-native-migr-alert"]',
                                 timeout_factor=completion_factor + 1)
        self.wait_assert_is_native(timeout_factor=completion_factor + 1)

    def wait_assert_is_native(self, **kw):
        wait_assert(lambda: self.api_get_field('vcs_type'),
                    lambda vcs_type: vcs_type == 'hg',
                    **kw)
        # wait should be minimal once VCS type is ok, no need to
        # forward timeout factor
        wait_assert(lambda: self.api_get_field('archived'),
                    lambda archived: not archived)

    def commit_page_url(self, commit_id):
        """Commit URL for regular (webdriver) navigation."""
        return '/'.join((self.url, '-', 'commit', commit_id))

    def archive_url(self, gitlab_branch, file_ext):
        base_file_name = '-'.join([self.name] + gitlab_branch.split('/'))
        return '/'.join((self.url,
                         '-', 'archive',
                         gitlab_branch,
                         base_file_name + '.' + file_ext
                         ))

    def get_archive(self, gitlab_branch, fmt='tar'):
        """Retrieve a repository archive by URL.

        :param fmt: the wished format. At this point, this is directly
            mapped as a file extension in the request, and only the `tar`
            value is tested.
        :returns: the archive content, as a files-like object
        """
        resp = requests.get(self.archive_url(gitlab_branch, fmt))
        assert resp.status_code == 200
        return BytesIO(resp.content)

    def webdriver_get_raw_blob(self, path, revision, webdriver=None):
        """Use a webdriver to download raw file content at a given revision.

        :param revision: anything that the Rails app understands, in
           particular GitLab branch name and commit hash.
        """
        if webdriver is None:
            webdriver = self.owner_webdriver

        webdriver.get('/'.join((self.url, '-', 'raw', revision, path)))
        return raw_page_content(webdriver)

    def webdriver_repo_new_content_menu(self, webdriver=None, refresh=False):
        if webdriver is None:
            webdriver = self.owner_webdriver

        if refresh or webdriver.current_url != self.url:
            webdriver.get(self.url)

        container = wait_element_visible(webdriver, By.XPATH,
                                         '//div[@data-testid="add-to-tree"]')
        wait_could_click_element(
            webdriver,
            lambda _d: container.find_element(
                By.XPATH,
                'button[@data-testid="base-dropdown-toggle"]')
        )
        wait_element_displayed(
            webdriver,
            lambda _d: container.find_element(By.XPATH, './/ul')
        )
        # each topmost <li> contains itself an <ul>, forcing `data-testid`
        # to only have the leaves.
        # also we need to retry, as sometimes rerenders occur between
        # lookup and text extraction
        attempt = 1
        while attempt < 3:
            lis = container.find_elements(
                By.XPATH, './/li[@data-testid="disclosure-dropdown-item"]')
            # The list items themselves contain either <a> or <button> elements
            # For now, returning just the texts will be enough
            try:
                return tuple(li.text.strip() for li in lis)
            except StaleElementReferenceException:
                attempt += 1

    def api_branches(self, empty_on_error=False):
        """Retrieve and pre-sort branches info through the REST API."""
        resp = self.api_get(subpath='repository/branches')
        if empty_on_error and resp.status_code >= 400:
            return {}

        assert resp.status_code == 200
        branches = resp.json()
        return dict((branch.pop('name'), branch) for branch in branches)

    def api_default_branch(self):
        branch = self.api_get_field('default_branch')
        assert branch is not None
        return branch

    def api_branch_titles(self):
        """Keep only commit titles from `api_branches()`

        With a test scenario in which those titles are characterizing the
        commit uniquely, this is what's very often needed for assertions.
        """
        return extract_gitlab_branch_titles(self.api_branches())

    def wait_assert_api_branches(self, condition,
                                 msg="The given condition on GitLab branches "
                                 "was still not fulfilled after retrying "
                                 "for {timeout} seconds",
                                 empty_on_error=False,
                                 **kwargs):
        """Assert some condition to become True on GitLab branches.

        Since the update of pushed or pruned branches is asynchronous and
        becomes even more so as GitLab progresses, this provides the means
        to retry several calls to :meth:`api_branches`.

        :param condition: any callable returning boolean that can take a
                          single argument, the payload of :meth:`api_branches`
        :param kwargs: passed to the underlying :func:`wait_assert` call.
        :returns: branches after the wait
        :raises: AssertionError if the condition doesn't become True before
                 timeout
        """
        return wait_assert(
            lambda: self.api_branches(empty_on_error=empty_on_error),
            condition,
            msg=msg,
            **kwargs
        )

    def wait_assert_api_branch_titles(self, expected, **kw):
        self.wait_assert_api_branches(
            lambda branches: (extract_gitlab_branch_titles(branches)
                              == expected),
            **kw,
        )

    def api_tags(self):
        """Retrieve and pre-sort tags info through the REST API."""
        resp = self.api_get(subpath='repository/tags')
        assert resp.status_code == 200
        tags = resp.json()
        return dict((tag.pop('name'), tag) for tag in tags)

    def api_protected_branches(self):
        resp = self.api_get(subpath='protected_branches')
        assert resp.status_code == 200
        return {br['name']: br for br in resp.json()}

    def api_unprotect_branch(self, branch_spec, check=True):
        """Unprotect the given branh specification.

        :param check: if ``True``, assert success. Otherwise return response.
        """
        resp = api_request('DELETE', self, self.owner_user,
                           subpath=protected_branch_api_subpath(branch_spec))
        if not check:
            return resp

        assert resp.status_code < 400

    def api_ensure_branch_is_unprotected(self, branch_spec, check=True):
        resp = self.api_unprotect_branch(branch_spec, check=False)
        if not check:
            return resp

        assert resp.status_code < 400 or resp.status_code == 404

    def api_protect_branch(self, branch_spec, check=True, **access_levels):
        """Create branch protection or update level.

        :param access_levels: a :class:`dict` with :class:`ProjectAccess`
           values
        """
        self.api_unprotect_branch(branch_spec)

        data = {k: level.value for k, level in access_levels.items()}
        data['name'] = branch_spec
        resp = api_request('POST', self, self.owner_user,
                           subpath=protected_branch_api_subpath(),
                           data=data)

        if not check:
            return resp

        assert resp.status_code < 400

    def api_commit(self, sha, check=True):
        """Retrieve a commit by its SHA.

        The SHA is the native one to GitLab, typically obtained through the
        API. For Mercurial SHAs, it's usually simpler to just perform a pull.
        """
        resp = self.api_get(subpath='repository/commits/' + sha)
        if not check:
            return resp

        assert resp.status_code == 200
        return resp.json()

    def api_file_create(self, path, user=None, check=True, **data):
        """data is transferred directly into the JSON expected by the API."""
        data['file_path'] = path
        resp = self.api_post(
            subpath='repository/files/' + path,
            user=user,
            data=data)
        if not check:
            return resp

        assert resp.status_code < 400
        return resp.json()

    def api_file_update(self, path, check=True, **data):
        """data is transferred directly into the JSON expected by the API."""
        data['file_path'] = path
        resp = self.api_put(
            subpath='repository/files/' + path,
            data=data)
        if not check:
            return resp

        assert resp.status_code < 400
        return resp.json()

    def api_wiki_page_create(self, user=None, check=True, **data):
        resp = self.user_api_request('POST', user=user,
                                     subpath='wikis', data=data)
        if not check:
            return resp
        assert resp.status_code == 201
        return resp.json()

    def api_wiki_page_get(self, slug, user=None, check=True):
        resp = self.user_api_request('GET', user=user,
                                     subpath='wikis/' + slug)
        if not check:
            return resp
        assert resp.status_code == 200
        return resp.json()

    def api_wiki_page_update(self, slug, user=None, check=True, **data):
        resp = self.user_api_request('PUT', user=user,
                                     subpath='wikis/' + slug,
                                     data=data)
        if not check:
            return resp
        assert resp.status_code == 200
        return resp.json()

    def api_wiki_pages_list(self, user=None, check=True):
        resp = self.user_api_request('GET', user=user, subpath='wikis')
        if not check:
            return resp
        assert resp.status_code == 200
        return resp.json()

    def hg_wiki_url(self, user_name=None):
        """Return an authenticated URL suitage for hg pull/push.

        :param user_name: any user name known to :attr:`heptapod`
        """
        if user_name is None:
            user_name = self.owner
        return self.basic_auth_url(user_name) + '.wiki'

    def api_file_get(self, path, ref, content_only=True):
        """Retrieve a repository file through API.

        :param content_only: if ``True``, the response status code is checked
           and the content is extracted and returned as
           bytes. Otherwise the full HTTP response is returned.
        """
        resp = self.api_get(subpath='repository/files/' + path,
                            params=dict(ref=ref))
        if not content_only:
            return resp

        assert resp.status_code == 200
        return b64decode(resp.json()['content'])

    def api_get_tree(self, ref=None, path='', check=True):
        resp = self.api_get(subpath='repository/tree',
                            params=dict(path=path))
        if not check:
            return resp

        return {entry['path']: dict(oid=entry['id'],
                                    obj_type=entry['type'],
                                    mode=entry['mode'],
                                    )
                for entry in resp.json()}

    def api_get_raw_blob(self, oid, check=True):
        resp = self.api_get(subpath=f'repository/blobs/{oid}/raw')
        if not check:
            return resp

        assert resp.status_code == 200
        return resp.text

    def webdriver_commit_raw(self, node, fmt, user=None):
        """Retrieve commit raw patch and diff."""
        if user is None:
            user = self.owner_user
        webdriver = user.webdriver
        webdriver.get(f'{self.url}/-/commit/{node}.{fmt}')
        return raw_page_content(webdriver)

    def api_file_delete(self, path, check=True, **data):
        data['file_path'] = path
        resp = self.api_delete(subpath='repository/files/' + path,
                               data=data)
        if not check:
            return resp

        assert resp.status_code < 400

    def webdriver_update_merge_request_settings(self, merge_method):
        driver = self.owner_webdriver
        driver.get(self.url + '/-/settings/merge_requests')
        input_id = 'project_merge_method_' + merge_method
        wait_could_click(driver, By.XPATH, f'//label[@for="{input_id}"]')
        wait_could_click_button(
            driver,
            type='submit',
            data_testid='save-merge-request-changes-button'
        )

    def webdriver_mercurial_settings(self, driver):
        driver.get(self.url + '/-/settings/repository')
        try:
            webdriver_expand_settings(driver, 'js-project-mercurial-settings')
        except TimeoutException:
            # previous section ID before the LayoutComponent refactoring
            # introduced with the native migration UI
            webdriver_expand_settings(driver, 'mercurial-settings')

    def webdriver_get_settings_page(self, page):
        """Go to the specified setttings page.

        :param page: last segment of the settings URL. Example: `ci_cd`
        :return: the webdriver, for caller convenience
        """
        driver = self.owner_webdriver
        driver.get('/'.join((self.url, '-', 'settings', page)))

        return driver

    def api_update_merge_request_settings(self, merge_method):
        resp = api_request('PUT', self, self.owner_user,
                           data=dict(merge_method=merge_method))
        assert resp.status_code < 400

    def api_fork(self, user, group=None):
        data = dict(id=self.id)
        if group is None:
            group = UserNameSpace(user_name=user.name, heptapod=self.heptapod)
        else:
            data['namespace_id'] = group.id

        resp = self.user_api_request('POST',
                                     user=user, subpath='fork', data=data)
        assert resp.status_code < 400

        fork_info = resp.json()
        owner_info = fork_info.get('owner')
        if owner_info is not None:
            assert owner_info['username'] == user.name
        fork = self.__class__(
            heptapod=self.heptapod,
            group=group, name=fork_info['path'],
            id=fork_info['id'],
            vcs_type=fork_info.get('vcs_type'),
            owner=user.name)
        return wait_assert(
            lambda: fork,
            lambda proj: proj.api_get_field('import_status') == 'finished'
        )

    def webdriver_fork(self, user):
        driver = user.webdriver
        driver.get(self.url)
        user_ns_id = user.personal_namespace.id
        wait_could_click(driver, By.XPATH, '//a[@data-testid="fork-button"]')
        wait_could_click(driver, By.XPATH,
                         '//div[@data-testid="select-namespace-dropdown"]'
                         '//button[@data-testid="base-dropdown-toggle"]')
        wait_could_click(
            driver, By.XPATH,
            '//li[@data-testid="listbox-item-gid://gitlab/Namespaces'
            f'::UserNamespace/{user_ns_id}"]'
        )

        wait_could_click_button(driver,
                                type='submit',
                                data_testid='fork-project-button')

        group = UserNameSpace(user_name=user.name, heptapod=self.heptapod)

        return wait_assert(
            lambda: self.api_retrieve(heptapod=self.heptapod,
                                      user_name=user.name,
                                      group=group,
                                      name=self.name,
                                      check=False),
            lambda fork: fork is not None
        )

    def api_create_merge_request(self, source,
                                 target='branch/default',
                                 **kwargs):
        """As the project owner, create a merge request through API.

        :param source: name of the source branch for GitLab, e.g.,
                    'topic/default/foo'
        :param target: name of the target branch for GitLab
        :param target_project: target :class:`Project` instance, defaults to
           ``self``, which is already the source project.
        :returns: numeric iid of the newly created MR
        """
        warnings.warn("Project.api_create_merge_request() is deprecated, "
                      "use MergeRequest.api_create() instead",
                      DeprecationWarning, stacklevel=2)
        return MergeRequest.api_create(self, source,
                                       target_branch=target,
                                       **kwargs).iid

    def api_create_deploy_token(self, name, scopes=('read_repository',)):
        """Will be available with GitLab 12.9."""
        resp = self.api_post(subpath='deploy_tokens',
                             data=dict(name=name,
                                       scopes=scopes))
        assert resp.status_code == 201
        return resp.json()

    def api_add_deploy_key(self, key,
                           can_push=False, title='heptapod-tests', **kw):
        resp = self.api_post(subpath='deploy_keys',
                             data=dict(key=key,
                                       can_push=can_push,
                                       title=title,
                                       **kw))
        assert resp.status_code == 201
        return resp.json()

    def api_delete_deploy_token(self, token):
        """Will be available with GitLab 12.9."""
        self.api_delete(subpath='deploy_tokens',
                        data=dict(token_id=token['id']))

    def webdriver_create_deploy_token(self, name):
        """Create a deploy token with Selenium

        The API doesn't exist before GitLab 12.9.
        This method does not work on GitLab 13.12 anymore. Probably not
        a big deal, but we can use the API instead for all current use cases.

        :param name: required by GitLab, is only a human intended description
        """
        driver = self.owner_webdriver
        driver.get(self.url + '/-/settings/repository')

        webdriver_expand_settings(driver, 'js-deploy-tokens')

        def name_elt(d):
            return d.find_element(By.ID, 'deploy_token_name')

        wait_element_displayed(driver, name_elt)

        name_elt(driver).send_keys(name)
        wait_could_click(driver, By.XPATH,
                         '//label[@for="deploy_token_read_repository"]')
        wait_could_click(driver, By.XPATH,
                         '//form[@id="new_deploy_token"]'
                         '//input[@type="submit"]')

        def value_for_id(elt_id):
            return driver.find_element(By.ID, elt_id).get_attribute('value')

        return dict(
            username=value_for_id('deploy-token-user'),
            token=value_for_id('deploy-token'),
        )

    def get_user_member(self, user_name=None, user=None, check=True):
        if user is None:
            user = self.heptapod.get_user(user_name)
        resp = self.api_get(subpath='members/%d' % user.id)
        if check:
            assert resp.status_code == 200
            return resp.json()

        return resp

    def wait_assert_user_member(self, user_name=None, user=None):
        return wait_assert(
            lambda: self.get_user_member(user_name=user_name,
                                         user=user,
                                         check=False),
            lambda resp: resp.status_code == 200).json()

    def grant_member_access(self, level, user_name=None, user=None):
        """Grant given user the given access level.

        It doesn't matter whether the user is already a member or not: this
        method abstracts over it.

        One of the `user_name` and `user` params has to be provided.

        This method is idempotent.
        """
        assert level in ProjectAccess

        if user is None:
            user = self.heptapod.get_user(user_name)

        user_id = user.id
        resp = self.api_get(subpath='members/%d' % user_id)
        if resp.status_code == 404:
            subpath = 'members'
            meth = 'POST'
        else:
            subpath = 'members/%d' % user_id
            meth = 'PUT'

        resp = api_request(meth, self, self.owner_user,
                           subpath=subpath,
                           data=dict(user_id=user_id, access_level=int(level)))
        assert resp.status_code < 400

    def load_tarball(self, tarball_path):
        """Replace server-side repository files by the contents of tarball.

        This should be used right after the project creation.

        :param Path tarball_path: path to an uncompressed tar
            archive containing `hg` and `git`. These
            will be renamed to the values of `self.fs_path`` and
            ``self.fs_path_git``.
        """
        if not self.heptapod.fs_access:
            raise NotImplementedError(
                "Can't use load_tarball() without filesystem access")

        # initialize repository
        # GitLab needs a first clone or push to consider the Git repository to
        # exist. Otherwise, local pushes such as what the heptapod sync hook
        # does just fail, with an error about the Git repo existence.
        tmpdir = py.path.local.mkdtemp()
        try:
            LocalRepo.clone(self.owner_basic_auth_url, tmpdir.join('clone'))
        finally:
            tmpdir.remove()

        heptapod = self.heptapod
        # using a temporary space in same mount point and unique enough
        srvtmpdir = self.fs_common_path + '.tmp'
        heptapod.run_shell(['rm', '-rf',
                            self.fs_path, self.fs_path_git, srvtmpdir])
        heptapod.run_shell(['mkdir', '-p', srvtmpdir])
        heptapod.put_archive(srvtmpdir, tarball_path)
        heptapod.run_shell(['mv', srvtmpdir + '/hg', self.fs_path])
        heptapod.run_shell(['mv', srvtmpdir + '/git', self.fs_path_git])

    def get_hgrc(self, managed=False):
        """Return repo's server-side HGRC, as lines, uid and gid

        :param managed: if ``True``, the contents returned are those of the
                        file managed by the Rails app, introduced
                        for heptapod#165
        """
        hgrc_path = '/'.join((self.fs_path, '.hg',
                              'hgrc.managed' if managed else 'hgrc'))
        return self.heptapod.get_file_lines(hgrc_path)

    def put_hgrc(self, lines, file_path='hgrc'):
        """Replace repo's server-side HGRC with given lines.

        The lines have to include LF, same as with `writelines()`.

        :param str file_path: relative path from the `.hg` directory of the
           repo for the file to rewrite. Allows to work on a different file
           than the main HGRC. Useful to manage secondary files (inclusions,
           clonebundles, configexpress…)
        """
        repo_inner_path = '/'.join((self.fs_path, '.hg'))

        return self.heptapod.put_file_lines(
            os.path.join(repo_inner_path, file_path), lines)

    def extend_hgrc(self, *lines):
        """Append given lines to repo's server-side HGRC

        The lines don't have to be newline-terminated.
        """
        hgrc_lines = self.get_hgrc()
        # just in case original hgrc isn't new-line terminated
        hgrc_lines.append('\n')
        hgrc_lines.extend(l + '\n' for l in lines)
        self.put_hgrc(hgrc_lines)

    def hg_config(self, section=None):
        """Return Mercurial configuration item, as really seen by hg process.

        In other words, this isn't inference on the contents of the various
        HGRC, it can be used to test propagation of config entries.

        :return: if ``section`` is passed, a simple ``dict``, otherwise a
                 ``dict`` of ``dicts``. End values are always strings.
        """
        cmd = [self.heptapod.hg_executable, '-R', self.fs_path,
               '--pager', 'false',
               'config']
        if section is not None:
            cmd.append(section)

        code, out = self.heptapod.execute(cmd, user='git')
        config = {}
        if out is None:
            return config
        for l in out.splitlines():
            print(l)
            fullkey, val = l.split('=', 1)
            section, key = fullkey.split('.', 1)
            if section is not None:
                config[key] = val
            else:
                config.setdefault(section, {})[key] = val
        return config

    def api_destroy(self, allow_missing=False, timeout_factor=1,
                    as_user=None):
        if as_user is None:
            as_user = self.owner  # just the owner name (str)

        if isinstance(as_user, str):
            as_user = self.heptapod.get_user(as_user)

        def delete(as_user):
            resp = requests.delete(self.api_url,
                                   headers=as_user.token_headers())
            if allow_missing and resp.status_code == 404:
                return
            print("DELETE request response: %r" % resp.json())
            assert resp.status_code == 202
            return resp

        def is_deleted():
            resp = self.api_get()
            if resp.status_code == 404:
                return True
            # deletion can start by renaming to ...-deleted-number
            new_path = resp.json()['path']
            split = new_path.rsplit('-', 2)
            if len(split) == 3 and split[1] == 'deleted':
                return True
            return False

        # Even though the deletion meaning that the repos are just
        # mv'ed on the filesystem, it is still async
        return wait_assert(
            lambda: delete(as_user),
            lambda _resp: is_deleted(),
            msg="Project %r was not destroyed (still accessible) after "
            "{timeout} seconds",
        )

    @classmethod
    def api_retrieve(cls, heptapod, user_name, group, name, check=True):
        """Retrieve Project instance if `id` is not known.

        :param user_name: name of an user having enough access to retrieve
                          project info and in particular owner name
        """
        project = cls(heptapod=heptapod,
                      owner=user_name,  # temporary
                      group=group,
                      name=name)
        resp = project.api_get()
        if check:
            assert resp.status_code == 200
        elif resp.status_code == 404:
            return

        data = cls.assert_project_info(resp, heptapod)
        project.vcs_type = data['vcs_type']
        project.id = data['id']
        creator_id = data.get('creator_id')
        owner = data.get('owner')
        if owner is not None:
            project.owner = data['owner']['username']
        elif creator_id is not None:
            project.creator_id = creator_id
        else:
            raise LookupError("No owner/creator information for %r", project)

        return project

    @classmethod
    def webdriver_create(cls, heptapod, user_name, project_name, **kwargs):
        """Create a new project with the webdriver for given user
        """
        group = UserNameSpace(heptapod=heptapod, user_name=user_name)
        driver = heptapod.get_user(user_name).webdriver
        driver.get('{url}/projects/new'.format(url=heptapod.url))
        cls.webdriver_new_project_submit(driver, project_name,
                                         vcs_type=heptapod.vcs_type,
                                         **kwargs)
        project = cls.api_retrieve(heptapod, user_name, group, project_name)

        project.wait_hg_availability()
        return project

    @classmethod
    def webdriver_import_url(cls, heptapod, user, project_name, url,
                             vcs_type=None,
                             wait_import_url_validation=True,
                             timeout_factor=3,
                             check_success=True,
                             **kwargs):
        """Import a new project with the webdriver for given user,

        The project will be in the user personal namespace.
        """
        group = UserNameSpace(heptapod=heptapod, user_name=user.name)
        driver = user.webdriver
        driver.get(heptapod.url + '/projects/new#import_project')
        url_input_spec = (By.NAME, 'project[import_url]')
        url_input = driver.find_element(*url_input_spec)
        if url_input.is_displayed():
            # we already are on the import form, probably because of a
            # previous test. Let's start over
            url_input.clear()
        else:
            url_button = driver.find_element(
                By.CSS_SELECTOR,
                'button.js-import-git-toggle-button')
            url_button.click()

        def fill_url(driver):
            elem = driver.find_element(*url_input_spec)
            elem.send_keys(url)
            if vcs_type is not None:
                # must wait for VCS type selection to be taken into account
                # (same comment as below about proper waiting)
                time.sleep(BASE_TIMEOUT / 10)
            elem.send_keys(Keys.TAB)
            if wait_import_url_validation:
                # proper waiting is hard to implement, because if validation
                # succeeds, nothing changes on the page, so there's no element
                # to wait on (typically in redisplay it would be a wait for
                # staleness of old element, then wait for apparition of new
                # element. There are several recipes online, most of them
                # relying on `jQuery.active`, which we can't assume to work.
                # Some other methods inject JavaScript that seems to add
                # further callbacks to XHRs… Too complicated for now.
                # So this is lame, but good enough to reproduce heptapod#524
                time.sleep(BASE_TIMEOUT / 10)

        if vcs_type is None:
            vcs_type = heptapod.vcs_type

        cls.webdriver_new_project_submit(driver, project_name,
                                         vcs_type=vcs_type,
                                         additional_driver_actions=fill_url,
                                         select_blank_project=False,
                                         # the hidden init README checkbox
                                         # is selected (and ignored), don't
                                         # try to toggle it.
                                         init_with_readme=True,
                                         assert_created_user_feedback=False,
                                         **kwargs)
        project = cls.api_retrieve(heptapod, user.name, group, project_name,
                                   check=check_success)
        if project is None:
            return NO_PROJECT
        project.wait_assert_import(timeout_factor=timeout_factor,
                                   check_success=check_success)
        return project

    def webdriver_import_errors(self, user=None):
        """Assert import error alert is on user current page, return details.

        This is to be used right after submitting an import form. By default,
        the project is expected to have been created, hence its owner should
        be on the import page with errors.

        :param user: defaults to `self.owner_user`, but can be overridden,
          e.g., for reimport attempts with a different user.
        :returns: (alert title, alert body)
        """
        if user is None:
            user = self.owner_user

        driver = user.webdriver

        def alert_selector(sub):
            """There are several alerts on the page, selecting the right one.

            The discriminating factor is that the one exposing the errors
            is non-dismissible.
            """
            return (By.CSS_SELECTOR,
                    f'.gl-alert-not-dismissible .gl-alert-{sub}')

        try:
            wait_element_visible(driver, *alert_selector('content'))
        except TimeoutException:
            raise AssertionError(
                "Import error alert not found in webdriver current page")

        title = driver.find_element(*alert_selector('title'))
        body = driver.find_element(*alert_selector('body'))
        return title.text, body.text

    def webdriver_assert_no_repo(self, user=None, check_buttons=False):
        """Navigate to the project and assert we get the "No repository" page.
        """
        if user is None:
            user = self.owner_user

        driver = user.webdriver
        driver.get(self.url)
        # we'll probably have to refine this down the road, another h2
        # could appear in the page and take precedence in this simple selector
        h2 = driver.find_element(By.XPATH, '//h2')
        assert h2.text.strip() == 'No repository'

        if not check_buttons:
            return

        for label in ("Create empty", "Import repository"):
            try:
                driver.find_element(By.XPATH,
                                    f'//a[contains(text(), "{label}")]')
            except NoSuchElementException:
                raise AssertionError(
                    f"Project home page does not contain link with '{label}'")

    def wait_hg_availability(self):
        wait_assert(lambda: self.owner_get(params=dict(cmd='capabilities')),
                    lambda resp: resp.status_code == 200)

    def wait_assert_user_visible(self, user):
        """Wait until the given user can see the project.

        On private projects, as of GitLab 15.4, adding a user to the members
        list does not immediately open access, hence tests will have to
        use this method to wait for it.
        """
        wait_assert(lambda: self.user_api_request('GET', user=user),
                    lambda r: r.status_code == 200)

    @classmethod
    def webdriver_new_project_submit(cls, driver, project_name,
                                     select_blank_project=True,
                                     additional_driver_actions=None,
                                     assert_created_user_feedback=True,
                                     vcs_type=None,
                                     import_url_validation=False,
                                     init_with_readme=False):
        """Create a new project while already on the "New project" page.

        This will put the project in the default namespace proposed by
        the "New project" page. We could add a `group` kwarg later on.
        """
        assert 'GitLab' in driver.title
        assert 'New Project' in driver.title

        if select_blank_project:
            webdriver_wait(driver).until(
                could_click_element(
                    lambda d: d.find_element(
                        By.XPATH,
                        '//a[@href = "#blank_project"]')))

        # the project path (slug) attribute is derived automatically from
        # its (human readable) name. The names given in these tests all
        # transform identically into paths.
        # In GitLab 12.10 the converse is true: if only the path is given,
        # the name is derived from it with some prettyfication (capitalization,
        # spaces). Therefore it is better for our needs to provide the name
        # only.
        elem = driver.find_element(By.NAME, 'project[name]')
        elem.send_keys(project_name)
        # If we wanted later on to make sure the path is the intended
        # one, we'd have to clear the `project[path]` field first, instead
        # of *adding* path after what was just prefilled due to
        # the setting of `project[name]`

        # in GitLab 14.2 the initialization with README is selected by default
        init_readme_checkbox = driver.find_element(
            By.ID,
            'project_initialize_with_readme')
        selected = init_readme_checkbox.get_attribute('selected') == 'true'
        if (not init_with_readme) is selected:
            # in GitLab 15.3, one must click on the label instead of the input
            driver.find_element(
                By.XPATH,
                '//label[@for="project_initialize_with_readme"]'
            ).click()

        if vcs_type is not None:
            option = driver.find_element(By.XPATH,
                                         '//select[@id="project_vcs_type"]'
                                         '//option[@value="%s"]' % vcs_type)
            option.click()

        if additional_driver_actions is not None:
            additional_driver_actions(driver)

        wait_could_click_button(driver,
                                timeout_factor=3,
                                type='submit',
                                data_testid='project-create-button')
        webdriver_wait(driver).until(
            lambda d: 'will automatically refresh' not in d.page_source)

        if not assert_created_user_feedback:
            return

        wait_assert_in_page_source(
            driver, f"Project '{project_name}' was successfully created.")

    @classmethod
    def webdriver_assert_import_form_url_error(cls, driver, expected=None):
        """Assuming the webdriver is on import form, assert URL error."""
        try:
            elt = driver.find_element(
                By.CSS_SELECTOR,
                'div.js-import-url-error div.gl-alert-body'
            )
        except NoSuchElementException:
            raise AssertionError("URL error not found in import form")
        else:
            if expected is not None:
                assert expected in elt.text

    def webdriver_retrieve(cls, driver, heptapod, group, name,
                           wait_availability=False):
        """Use a driver to retrieve the project if it exists.

        If the project is not found (could happen with authnz problems),
        then `None` is returned.
        """
        project = Project(heptapod=heptapod, group=group, name=name)
        resp = project.session_api_get(driver)

        if resp.status_code == 404:
            return

        data = resp.json()
        project.owner = data['owner']['username']
        project.id = data['id']
        return project

    @classmethod
    def api_create(cls, heptapod, user_name, project_name,
                   group=None, timeout_factor=3, **data):
        """Create project using the RESTful API.

        :param user_name: name of the user to run the import with
        :param group: name of the project group (by default, will be
                      user personal space.
        :param data: for extra data in the POST API request that performs
                     the creation
        :returns: Project instance
        """
        if group is None:
            group = UserNameSpace(heptapod=heptapod, user_name=user_name)
        else:
            data['namespace_id'] = group.id
        group_path = group.full_path

        headers = heptapod.get_user(user_name).token_headers()

        data['name'] = project_name
        url = heptapod.url + '/api/v4/projects'

        data.setdefault('vcs_type', heptapod.vcs_type)

        def post():
            return requests.post(url, headers=headers, data=data)

        def needs_retry(response):
            if response is None:
                return True
            if response.status_code != 400:
                return False
            structured = response.json()
            message = structured.get('message', {})

            if ['has already been taken'] in (message.get('name'),
                                              message.get('path')):
                # clean up if we can
                try:
                    route = '/'.join((group_path, project_name))
                    logger.warn("GitLab Route %r has already been taken, "
                                "attempting to remove it", route)
                    heptapod.force_remove_route(route)
                except NotImplementedError:
                    pass

                # trigger retry even if we can't clean up from here:
                # on GitLab 12, there's a short timespan after it stops
                # telling us to retry but before it has fully cleaned up routes
                return True

            if any('try again' in l for l in message.get('base', ())):
                logger.info(
                    "Got explicit retry response: %r with headers %r",
                    structured, response.headers)
                return True

        resp = wait_assert(post, lambda resp: not needs_retry(resp),
                           timeout_factor=timeout_factor,
                           msg="Project could not be created "
                           "in {timeout} seconds",
                           )

        logger.debug("Creation request response: %r", resp.json())
        assert resp.status_code in (200, 201)

        vcs_type = data['vcs_type']
        proj_info = cls.assert_project_info(resp, heptapod,
                                            owner_name=user_name,
                                            vcs_type=vcs_type)

        return cls(heptapod=heptapod,
                   group=group, name=project_name,
                   id=proj_info['id'],
                   vcs_type=vcs_type,
                   hg_git_repo_expected=vcs_type == 'hg_git',
                   owner=user_name)

    @classmethod
    def assert_project_info(cls, api_resp, heptapod,
                            owner_name=None,
                            vcs_type=None):
        """Check that defining fields are as expected in an API response

        :returns: project info dict, as given by API response
        """
        proj_info = api_resp.json()
        if owner_name is not None:
            owner_info = proj_info.get('owner')
            if owner_info is not None:
                assert owner_info['username'] == owner_name

        if vcs_type is not None:
            assert proj_info['vcs_type'] == vcs_type
        if proj_info['vcs_type'] == 'hg':
            # this seems tautological now that conversion to Git has been
            # removed for native repositories, but it is a good catcher of
            # discrepancies, either in Rails or in these tests.
            assert proj_info['hg_without_git'] is True

        return proj_info

    @classmethod
    def api_import_url(cls, heptapod, user, project_name, url,
                       group=None, **wait_assert_kw):
        """Import project from URL, wait for completion and returns it.

        :param user_name: name of the user to run the import with
        :param group: name of the project group (by default, will be
                      user personal space.
        :returns: import_status ('failed' or 'finished'), import_error,
                  Project instance
        """
        project = cls.api_create(heptapod, user.name, project_name,
                                 group=group,
                                 import_url=url)
        project.wait_assert_import(**wait_assert_kw)
        return project

    def wait_assert_import(self, timeout_factor=3, check_success=True):
        unexpected_statuses = (None, 'none')
        terminal_statuses = ('finished', 'failed')

        def status_is_terminal(proj_info):
            status = proj_info['import_status']
            if status in terminal_statuses:
                return True
            assert status not in unexpected_statuses

        proj_info = wait_assert(
            lambda: self.api_get_info(),
            lambda proj_info: proj_info['import_status'] in terminal_statuses,
            msg="Import was still running after {timeout} seconds",
            timeout_factor=timeout_factor,
        )
        if not check_success:
            return proj_info

        if proj_info['import_status'] == 'failed':
            raise AssertionError(proj_info.get('import_error'))

        print("Project information after import or timeout: \n%r" % proj_info)

    @classmethod
    def api_import_tarball(cls, heptapod, user_name,
                           project_name, tarball_fobj,
                           group=None,
                           timeout_factor=3,
                           retry_wait_factor=0.05,
                           ):
        """Import project from a tarball, wait for completion and returns it.

        :param user_name: name of the user to run the import with
        :param group: name of the project group (by default, will be
                      user personal space.
        :param tarball_fobj: open file-like object for the tarball to import
        :returns: Project instance
        """
        user = heptapod.get_user(user_name)
        headers = user.token_headers()
        data = dict(path=project_name)

        if group is None:
            group = UserNameSpace(heptapod=heptapod, user_name=user_name)
        else:
            data['namespace_id'] = group.id

        resp = requests.post(heptapod.url + '/api/v4/projects/import',
                             headers=headers,
                             data=data,
                             files=dict(file=('proj.tar.gz', tarball_fobj)))
        assert resp.status_code < 400

        proj_info = resp.json()
        proj = cls(heptapod=heptapod,
                   group=group, name=project_name,
                   id=proj_info['id'],
                   # proj_info['vcs_type'] is at this point just a default one
                   # that the import process will correct from information
                   # in the tarball.
                   owner=user_name)

        resp = wait_assert(
            lambda: proj.api_get(subpath='import'),
            lambda resp: (resp.status_code < 400
                          and resp.json()['import_status'] == 'finished'),
            timeout_factor=timeout_factor,
            retry_wait_factor=retry_wait_factor,
            msg="Import not finished in {timeout} seconds",
        )
        proj.vcs_type = resp.json()['vcs_type']
        return proj

    @classmethod
    def api_list(cls, heptapod, search_as='root', **params):
        """List the projects owned by the given user

        Does not support batching at this point, hence will work only
        if the result set fits in the first page.

        Various filtering criteria can be applied, hence it is more a search
        than a listing (notably ``search=something`` is possible)

        :param search_as: login name of the user to perform the listing.
                          Must be one of those registered to the
                          :class:`Heptapod` instance.
        """
        resp = requests.get(
            heptapod.api_url + '/projects',
            headers=heptapod.get_user(search_as).token_headers(),
            params=params
        )
        return resp

    def api_transfer(self, group):
        # API for regular users (on the project) has been introduced in
        # GitLab 11.1 (see https://docs.gitlab.com/ce/api/projects.html)
        # but in current GitLab, root can do it
        heptapod = self.heptapod
        resp = requests.post(
            '{api}/groups/{group.id}/projects/{proj.id}'.format(
                api=heptapod.api_url, group=group, proj=self),
            headers=heptapod.get_user('root').token_headers(),
        )
        if resp.status_code < 400:
            # let's have in particular correct subsequent URLs
            self.group = group
            if self.is_legacy:
                # path on disk actually changes for legacy projects
                self._disk_path = None
        return resp

    def api_export(self, target_fobj,
                   timeout_factor=3, retry_wait_factor=0.05
                   ):
        """Export the project in a given file

        This is synchronous from caller's perspective.

        :target_fobj: a writable, binary, file-like object.
        """
        resp = self.api_post(subpath='export')
        assert resp.status_code == 202

        wait_assert(
            lambda: self.api_get(subpath='export'),
            lambda resp: (resp.status_code < 400
                          and resp.json()['export_status'] == 'finished'),
            timeout_factor=timeout_factor,
            retry_wait_factor=retry_wait_factor,
            msg="Export not finished in {timeout} seconds",
        )

        resp = self.api_get(subpath='export/download', stream=True)
        assert resp.status_code == 200
        for chunk in resp.iter_content(chunk_size=8192):
            target_fobj.write(chunk)

    def only_specific_runners(self):
        resp = self.api_edit(shared_runners_enabled=False)
        assert resp.status_code < 400

        if resp.json()['namespace']['kind'] != 'group':
            return

        resp = self.api_edit(group_runners_enabled=False)
        assert resp.status_code < 400

    def only_instance_runners(self):
        resp = self.api_edit(group_runners_enabled=False,
                             shared_runners_enabled=True)
        assert resp.status_code < 400

    def only_group_runners(self):
        resp = self.api_edit(group_runners_enabled=True,
                             shared_runners_enabled=False)
        assert resp.status_code < 400

    def get_job_artifacts(self, job):
        """Return filename, artifacts (archive) as bytes."""
        resp = self.api_get(subpath='jobs/%d/artifacts' % job['id'])
        assert resp.status_code == 200
        # Finding file name depends on redirections (S3 etc.)
        # if we need something more precise, the 302 response is available
        # in resp.history
        if resp.url.startswith(self.heptapod.url):
            # no redirection, filename is in `Content-Disposition`
            # Not fully compliant filename parsing.
            # Full specification: RFC 6266.
            # there's an unsupported lib on PyPI for this (rfc6266)
            m = re.match(r'attachment; filename="(.*?)";',
                         resp.headers['Content-Disposition'])
            assert m is not None
            filename = m.group(1)
        else:
            # redirection, let's check that it is to a S3 storage backend.
            query_params = parse_qs(urlparse(resp.url).query)
            assert 'X-Amz-Credential' in query_params
            # the filename is just a content hash, it is not per se interesting
            filename = 'S3 content hash'

        return filename, resp.content

    def api_jobs(self, check=True):
        """Return CI jobs, per commit ID.

        The result is a :class:`dict` whose keys are GitLab commit IDs
        (Git or Mercurial SHA depending on VCS type) and values lists
        of jobs, expressed themselves as data dicts.
        """
        resp = self.api_get(subpath='jobs')
        if not check:
            return resp

        assert resp.status_code == 200
        jobs = {}
        for job in resp.json():
            jobs.setdefault(job['commit']['id'], []).append(job)
        return jobs

    def api_get_job(self, job_id, check=True):
        resp = self.api_get(subpath='jobs/' + str(job_id))
        if not check:
            return resp

        assert resp.status_code == 200
        return resp.json()

    def wait_assert_jobs_for_commit(self, commit_id, **wait_kw):
        jobs = wait_assert(lambda: self.api_jobs(),
                           lambda jobs: commit_id in jobs,
                           **wait_kw)
        return jobs[commit_id]

    def wait_assert_job(self, job_id, condition, **wait_kw):
        return wait_assert(lambda: self.api_get_job(job_id),
                           condition, **wait_kw)

    def api_create_pipeline_trigger_token(self, check=True,
                                          description='hpd-tests'):
        """Create and return a CI trigger token or the response.

        :param check: if ``True``, assert response code and return token,
           else return response.
        :param description: the token description (to avoid collisions if
           needed).
        """
        resp = api_request('POST', self,
                           user=self.owner_user,
                           subpath='triggers',
                           data=dict(description="hpd-tests"))
        if not check:
            return resp

        assert resp.status_code == 201
        return resp.json()['token']

    def api_create_mirror(self, **params):
        return ProjectMirror.api_create(self, **params)

    def api_list_mirrors(self, check=True):
        """Return a list of dicts, not of ProjectMirror instances.

        The reason is that ProjectMirror currently does not keep more
        state than that's needed for identification.
        """
        resp = self.api_get(subpath='remote_mirrors')
        if not check:
            return resp

        assert resp.status_code < 300
        return resp.json()

    def assert_no_unwanted_git_repo(self):
        heptapod = self.heptapod
        if not heptapod.fs_access:
            # we can't assert
            return

        if self.vcs_type == 'hg':
            assert not heptapod.path_exists(self.fs_path_git_legacy())
            if not self.hg_git_repo_expected:
                assert not heptapod.path_exists(self.fs_path_git)

    def __enter__(self):
        return self

    def __exit__(self, *exc_args):
        # let's give a bit more time than usual: this is used for
        # cleanups and the instance could be recovering from various errors
        self.api_destroy(allow_missing=True, timeout_factor=3)
        return False


class NoProject:
    """A context manager object to return to express absence of a Project.

    The simplest way for creation / retrieval methods would be to return
    ``None``. However, this is not practical when expecting a context manager
    as in, e.g., ::

        with Project.some_method(*a, **kw) as project:
            if project is None:
               ...

    Therefore if the method returns this context manager, then the above
    code block will work.

    It is recommended to return the `NO_PROJECT` singleton, so that this also
    works::

       project = Project.some_method(*a, **kw)
       if project is NO_PROJECT:
           ...
    """

    def __enter__(self):
        return None

    def __exit__(self, *exc_args):
        return False


NO_PROJECT = NoProject()
