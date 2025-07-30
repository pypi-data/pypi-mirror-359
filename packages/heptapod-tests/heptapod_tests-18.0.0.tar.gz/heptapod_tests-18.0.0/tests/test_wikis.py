from pathlib import Path
from selenium.webdriver.common.by import By

from heptapod_tests.hg import LocalRepo
from heptapod_tests.selenium import (
    wait_element_visible,
)
from . import needs


def assert_wiki_page_h1(project, slug, text):
    webdriver = project.owner_webdriver
    webdriver.get(project.url + '/-/wikis/' + slug)
    elt = wait_element_visible(webdriver, By.XPATH,
                               '//*[@data-testid="wiki-page-content"]//h1')
    assert elt.text.strip() == text.strip()


def test_wiki_basic(test_project, tmpdir):
    """ A basic scenario: create, get, update, clone, push."""
    proj = test_project
    info = proj.api_wiki_page_create(title="Home", content="# Sweet home")
    assert info['title'] == "Home"
    # properly rendered as markdown (the default)
    assert_wiki_page_h1(proj, info['slug'], "Sweet home")

    clone_path = tmpdir.join('clone')
    clone = LocalRepo.clone(proj.hg_wiki_url(), clone_path)
    assert clone_path.join('Home.md').read() == '# Sweet home'

    clone_path.join('howto.rst').write(
        '\n'.join((
            "Howto",
            "=====",
        )))
    clone.hg('ci', '-Am', "reStructured")
    clone.hg('push')

    pages = proj.api_wiki_pages_list()
    assert {(p['slug'], p['format']) for p in pages} == {
        ("Home", 'markdown'),
        ("howto", 'rest'),
    }

    assert_wiki_page_h1(proj, "howto", "Howto")

    update = dict(slug='Home',
                  content="# is not like outdoors",
                  title="Home")
    proj.api_wiki_page_update(**update)
    assert_wiki_page_h1(proj, 'Home', "is not like outdoors")

    # an update with no change should not give error (heptapod#1988)
    proj.api_wiki_page_update(**update)

    # let's pull/push over SSH this time
    ssh_cmd, ssh_url = proj.owner_ssh_params
    ssh_url = ssh_url.replace('.hg', '.wiki')

    clone.hg('pull', '--ssh', ssh_cmd, ssh_url, '-u')

    assert clone_path.join('Home.md').read() == '# is not like outdoors'

    clone.hg('rm', 'howto.rst')
    clone.hg('commit', '-m', "removing a page by a push")
    clone.hg('push', '--ssh', ssh_cmd, ssh_url)
    pages = proj.api_wiki_pages_list()
    assert {(p['slug'], p['format']) for p in pages} == {
        ("Home", 'markdown'),
    }


@needs.hg_native
@needs.fs_access
def test_native_wiki_issue_1987(test_project, tmpdir):
    proj = test_project
    info = proj.api_wiki_page_create(title="Home", content="# Sweet home")

    # Prerequisites: wiki worked as expected
    assert info['title'] == "Home"
    gl_default_branch_path = Path(test_project.fs_common_path
                                  + '.wiki.hg/.hg/default_gitlab_branch')

    def assert_gl_default_branch():
        assert gl_default_branch_path.read_bytes() == b'branch/default'

    assert_gl_default_branch()

    # Now removing the default branch file to simulate what happened if
    # it started as a hg-git based Wiki
    gl_default_branch_path.unlink()

    info = proj.api_wiki_page_create(title="Contact", content="# Call home")
    assert info['title'] == "Contact"
    assert_gl_default_branch()
