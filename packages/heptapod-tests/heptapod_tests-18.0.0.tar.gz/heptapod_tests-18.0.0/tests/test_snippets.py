from heptapod_tests.git import LocalRepo as GitRepo
from heptapod_tests.wait import wait_assert


def wait_assert_html_contains(driver, url, expected, **wait_kw):
    """Wait until the expected string is in the HTML source at URL."""
    wait_assert(lambda: driver.get(url),
                lambda _: expected in driver.page_source,
                **wait_kw)


def test_project_snippets(test_project, tmpdir):
    project = test_project
    tex = r"\sum_{k=0}^n k = \frac{n(n+1)}{2}"
    resp = project.api_post(
        subpath='snippets',
        data=dict(file_name='snip.tex',
                  title="Triangular numbers",
                  description="First snippet",
                  content=tex,
                  visibility="private"))
    assert resp.status_code == 201
    info = resp.json()

    snippet_id = info['id']
    assert info['title'] == "Triangular numbers"
    assert info['visibility'] == "private"
    assert info['project_id'] == project.id
    assert info['file_name'] == 'snip.tex'

    webdriver = test_project.owner_webdriver
    snippet_uri = 'snippets/%d' % snippet_id
    raw_content_url = '/'.join((test_project.url, snippet_uri, '/raw'))
    wait_assert_html_contains(webdriver, raw_content_url, tex)

    ssh_cmd, ssh_url = test_project.owner_ssh_params
    ssh_url = ssh_url.rsplit('.', 1)[0] + '/snippets/%d.git' % snippet_id

    ssh_clone_path = tmpdir.join('ssh_clone')
    ssh_clone = GitRepo.clone(ssh_url, ssh_clone_path, ssh_cmd=ssh_cmd)
    ssh_content_path = ssh_clone_path.join('snip.tex')
    assert ssh_content_path.exists()
    assert ssh_content_path.read() == tex

    tex2 = r"\sum_{k=0}^n k = n(n+1)/2"
    ssh_content_path.write(tex2)
    ssh_clone.git("commit", "-am", "Better version for inlining")
    ssh_clone.git("push", ssh_cmd=ssh_cmd)

    http_url = '/'.join((test_project.owner_basic_auth_url, snippet_uri))
    http_clone_path = tmpdir.join('http_clone')
    http_clone = GitRepo.clone(http_url, http_clone_path)

    http_content_path = http_clone_path.join('snip.tex')
    assert http_content_path.exists()
    assert http_content_path.read() == tex2

    tex3 = r"pairs(n) = n(n-1)/2"
    http_content_path.write(tex3)
    http_clone.git("commit", "-am", "Pairs also")
    http_clone.git("push")

    ssh_clone.git("pull", ssh_cmd=ssh_cmd)
    assert ssh_content_path.read() == tex3

    wait_assert_html_contains(webdriver, raw_content_url, tex3,
                              timeout_factor=10)


def test_personal_snippets(heptapod, tmpdir):
    basic_user = heptapod.get_user('test_basic')
    tex = r"\sum_{k=0}^n k = \frac{n(n+1)}{2}"
    resp = heptapod.api_post(user=basic_user,
                             subpath='snippets',
                             data=dict(file_name='snip.tex',
                                       title="Triangular numbers",
                                       description="First snippet",
                                       content=tex,
                                       visibility="private"))
    assert resp.status_code == 201
    info = resp.json()

    snippet_id = info['id']
    assert info['title'] == "Triangular numbers"
    assert info['visibility'] == "private"
    assert info['file_name'] == 'snip.tex'

    webdriver = basic_user.webdriver
    snippet_uri = 'snippets/%d' % snippet_id
    raw_content_url = '/'.join((heptapod.url, snippet_uri, '/raw'))
    webdriver.get(raw_content_url)
    wait_assert_html_contains(webdriver, raw_content_url, tex)

    ssh_cmd = basic_user.ssh_command
    ssh_url = '/'.join((heptapod.ssh_url, snippet_uri + '.git'))

    ssh_clone_path = tmpdir.join('ssh_clone')
    ssh_clone = GitRepo.clone(ssh_url, ssh_clone_path, ssh_cmd=ssh_cmd)
    ssh_content_path = ssh_clone_path.join('snip.tex')
    assert ssh_content_path.exists()
    assert ssh_content_path.read() == tex

    tex2 = r"\sum_{k=0}^n k = n(n+1)/2"
    ssh_content_path.write(tex2)
    ssh_clone.git("commit", "-am", "Better version for inlining")
    ssh_clone.git("push", ssh_cmd=ssh_cmd)

    http_url = '/'.join((basic_user.basic_auth_url, snippet_uri + '.git'))
    http_clone_path = tmpdir.join('http_clone')
    http_clone = GitRepo.clone(http_url, http_clone_path)

    http_content_path = http_clone_path.join('snip.tex')
    assert http_content_path.exists()
    assert http_content_path.read() == tex2

    tex3 = r"pairs(n) = n(n-1)/2"
    http_content_path.write(tex3)
    http_clone.git("commit", "-am", "Pairs also")
    http_clone.git("push")

    ssh_clone.git("pull", ssh_cmd=ssh_cmd)
    assert ssh_content_path.read() == tex3

    webdriver.get(raw_content_url)
    wait_assert_html_contains(webdriver, raw_content_url, tex3,
                              timeout_factor=10)
