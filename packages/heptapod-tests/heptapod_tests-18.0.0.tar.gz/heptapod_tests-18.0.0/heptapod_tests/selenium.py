# Copyright 2019-2022 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 3 or any later version.
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Shared Selenium utils."""

from contextlib import contextmanager
import logging
import time
from selenium.common.exceptions import (
    ElementNotVisibleException,
    ElementNotInteractableException,
    NoSuchElementException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

from heptapod_tests.wait import (
    BASE_TIMEOUT,
    wait_assert,
)

logger = logging.getLogger(__name__)

WAIT_OPTIONS = ('retry_delay', 'timeout_factor')
SELENIUM_DEFAULT_WAIT_SLEEP = 0.5


@contextmanager
def window_size(driver, width, height):
    original = driver.get_window_size()

    driver.set_window_size(width=width, height=height)
    try:
        yield
    finally:
        driver.set_window_size(**original)


def page_means_not_ready(driver):
    """Detect a few symptoms of Heptapod not fully ready"""
    if '502' in driver.title:
        return True
    if 'Gitlab::Webpack::Manifest::ManifestLoadError' in driver.title:
        return True
    return False


def raw_page_content(driver):
    """Extract the content of a page meant for GitLab raw downloads.

    The webdriver rewraps it into a HTML ``pre`` element.
    """
    try:
        return driver.find_element(By.TAG_NAME, 'pre').text
    except NoSuchElementException:
        raise AssertionError("Page is empty or not a GitLab raw page")


def webdriver_wait_get(heptapod, driver,
                       relative_uri='', timeout=300, retry_delay=1):
    """Get the given URL when it's ready.

    At this stage, we already got the 302 on the site base URL, it's not
    clear why we can still get 502s, maybe just because that's harder
    that the simple redirection. Anyway, that justifies a shorter timeout
    by default than the initial one.
    """
    url = heptapod.url + relative_uri
    start = time.time()
    dead_msg = ("Heptapod server did not give a successful response"
                "in %s seconds" % timeout)
    while True:
        if time.time() > start + timeout:
            heptapod.dead = True  # will abort subsequent tests
        driver.get(url)
        if not page_means_not_ready(driver):
            break
        logger.debug("Title of page at %r is %r, retrying in %.1f seconds",
                     url, driver.title, retry_delay)
        time.sleep(retry_delay)
    assert not heptapod.dead, dead_msg


def could_click_element(selector):
    def try_click_element(driver):
        try:
            elem = selector(driver)
            elem.click()
            return True
        except (ElementNotVisibleException,
                NoSuchElementException,
                ElementNotInteractableException):
            return False
        except Exception:
            import traceback
            traceback.print_exc()
            return False
    return try_click_element


def webdriver_wait(driver, timeout_factor=1):
    return WebDriverWait(
        driver, BASE_TIMEOUT * timeout_factor,
        poll_frequency=SELENIUM_DEFAULT_WAIT_SLEEP * timeout_factor)


def wait_could_click_element(driver, selector, **wait_kw):
    """Wait until the element returned by selector could be clicked on.

    :param selector: a callable taking the driver as unique argument and
      returning the element, raising standard Selenium exceptions as
      expected in :func:`could_click_element`
    """
    webdriver_wait(driver, **wait_kw).until(could_click_element(selector))


def wait_could_click(driver, by, selector, **wait_kw):
    """Wait until the specified element could be clicked on.

    The ``By`` and ``selector`` arguments are as in ``driver.find_element()``.
    """
    return wait_could_click_element(driver,
                                    lambda d: d.find_element(by, selector),
                                    **wait_kw)


def wait_could_click_button(driver, **kw):
    """Shortcut to click on button when ready, with narrowing by attributes.

    :param kw: can contain the same options as :func:`webdriver_wait`. All
      other items are interpreted as attribute values with name converted to
      dashes instead of underscores (the latter supported for caller
      convenience). No escaping of values is performed but that should be
      good enough for the likes of `data-qa-selector`.
    """
    wait_kw = {}
    for k in WAIT_OPTIONS:
        v = kw.pop(k, None)
        if v is not None:
            wait_kw[k] = v

    attrs_expr = ' and '.join(f'@{k.replace("_", "-")}="{v}"'
                              for k, v in kw.items())
    return wait_could_click(driver, By.XPATH, f'//button[{attrs_expr}]',
                            **wait_kw)


def wait_element_displayed(driver, selector, **wait_kw):
    webdriver_wait(driver, **wait_kw).until(
        lambda d: selector(d).is_displayed())


def wait_element_visible(driver, loc_by, loc_expr, **wait_kw):
    return webdriver_wait(driver, **wait_kw).until(
        ec.visibility_of_element_located((loc_by, loc_expr))
    )


def wait_assert_in_page_source(driver, s):
    """Wait until the given string is in page source.

    Avoid doubts with eager evaluation of `driver.page_source` (would not
    happen in a lambda, but still).
    """
    wait_assert(lambda: driver.page_source,
                lambda source: s in source)


def assert_webdriver_not_error(webdriver):
    """assert that the current page is not GitLab's error page rendering.

    We don't have a reliable way to detect an error
    The page title would be just 500 in production and the error class name in
    # development mode.
    """
    title = webdriver.title
    assert "Error" not in title
    assert not any(("(%d)" % code) in title
                   for code in (500, 502, 504, 403, 404))


def webdriver_expand_settings(driver, section_id):
    """Expand the section with given identifier of a Settings page.


    This is meant for Project and Group settings and assumes that the
    webdriver is already on the Settings page.

    :param name: HTML id of the section, often but now always prefixed by
      ``js-``, e.g., 'js-merge-request-settings'
    :return: the XPATH expression for the section, for further use, e.g.,
        finding a submit button inside the section.
    """
    section_xpath = f'//section[@id="{section_id}"]'

    def toggle_button(driver, button_text):
        buttons = driver.find_elements(By.XPATH,
                                       section_xpath + '//button')
        # there are subtle differences between XPATH text() and
        # the text attribute of Selenium elements.
        return [btn for btn in buttons
                if button_text in btn.text.lower().strip()
                ][0]

    wait_could_click_element(driver, lambda d: toggle_button(d, 'expand'))
    wait_element_displayed(driver, lambda d: toggle_button(d, 'collapse'))

    return section_xpath
