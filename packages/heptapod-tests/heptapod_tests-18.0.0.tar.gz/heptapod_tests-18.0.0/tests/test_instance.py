"""Instance-wide tests that don't involve version control, nor a project."""

import re

from heptapod_tests.user import User
from heptapod_tests.utils import unique_name

DOTTED_VERSION_RE = r'\d+\.\d+(\.\d+)?'


def assert_webdriver_get(webdriver, url):
    """Get the given URL in webdriver and assert it's not broken"""
    webdriver.get(url)
    assert '(500)' not in webdriver.title


def test_help_page(heptapod):
    webdriver = heptapod.get_user('test_basic').webdriver
    webdriver.get(heptapod.url + '/help')

    assert '500' not in webdriver.title
    html = webdriver.page_source

    assert re.search(r'GitLab CE\s+' + DOTTED_VERSION_RE, html)
    assert re.search(r'Mercurial\s+' + DOTTED_VERSION_RE, html)
    assert re.search(r'Heptapod\s+(<span(.*?)>)?' + DOTTED_VERSION_RE, html)


def test_help_page_anonymous(heptapod):
    webdriver = None
    try:
        webdriver = heptapod.new_webdriver()
        webdriver.get(heptapod.url + '/help')
        assert '500' not in webdriver.title
        html = webdriver.page_source

        assert 'Heptapod' in html
        # in particular double check that this was really anonymous
        assert not re.search(r'Mercurial\s+' + DOTTED_VERSION_RE, html)
    finally:
        if webdriver is not None:
            webdriver.close()


def test_admin_views(heptapod):
    webdriver = heptapod.get_user('root').webdriver
    for slug in (
            'application_settings/general',
            'users',
    ):
        assert_webdriver_get(webdriver, '/'.join(
            (heptapod.url, 'admin', slug)))

    try:
        user = User.create(heptapod, unique_name('test_admin_view'))
        user_admin_url = '/'.join((heptapod.url, 'admin', 'users', user.name))
        assert_webdriver_get(webdriver, user_admin_url)

        user.block()
        assert_webdriver_get(webdriver, user_admin_url)

        user.unblock()
        user.deactivate()
        assert_webdriver_get(webdriver, user_admin_url)
    finally:
        user.delete()
