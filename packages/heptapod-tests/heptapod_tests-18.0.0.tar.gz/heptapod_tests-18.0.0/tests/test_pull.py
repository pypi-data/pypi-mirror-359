from heptapod_tests.hg import LocalRepo
# TODO make a fixture from that:
from .test_push import prepare_simple_repo

from . import needs

ENABLE_CONFIG_EXPRESS = ('--config', 'extensions.configexpress=')
DISABLE_CONFIG_EXPRESS = ('--config', 'extensions.configexpress=!')


def test_configexpress_no_proposition(test_project, tmpdir):
    """Check configexpress output from the client-side (always on stderr)
    """
    url = test_project.owner_basic_auth_url
    clone = LocalRepo.clone(url, tmpdir.join('repo2'))
    prepare_simple_repo(test_project, tmpdir.join('repo1'))
    # let's control what GitLab really sees
    # for this test, we don't want to depend on the fact that the current
    # version of configexpress does not care whether the repo is empty or not
    assert test_project.api_branch_titles() == {
        'branch/default': 'Commit 0',
        'topic/default/zetop': 'Commit 1',
    }

    # a client without configexpress doesn't see anything special
    code, _, err = clone.hg_unchecked('pull', *DISABLE_CONFIG_EXPRESS)
    assert code == 0
    assert not err.strip()

    code, _, err = clone.hg_unchecked('pull', *ENABLE_CONFIG_EXPRESS)
    assert code == 0
    assert not err.strip()


@needs.fs_access
def test_configexpress_server_proposition(test_project, tmpdir):
    """Check configexpress output from the client-side (always on stderr)
    """
    # we don't even need content in the server-side repo
    clone = LocalRepo.clone(test_project.owner_basic_auth_url,
                            tmpdir.join('clone'))

    suggestions = ("[express-suggestions]\n", "animal=ant\n")
    test_project.put_hgrc(suggestions, file_path='express.hgrc')
    test_project.extend_hgrc("\n",
                             "[configexpress:server2client]\n",
                             "express-suggestions=express.hgrc\n"
                             )

    # a client without configexpress doesn't see anything special
    code, _, err = clone.hg_unchecked('pull', *DISABLE_CONFIG_EXPRESS)
    assert code == 0
    assert not err.strip()

    code, _, err = clone.hg_unchecked('pull', *ENABLE_CONFIG_EXPRESS)
    assert code == 0
    lines = err.splitlines()

    # skip preamble without relying on its contents nor its length
    while suggestions[0].strip() != lines[0].strip():
        lines = lines[1:]
    assert lines, "Did not detect configexpress output"

    assert all(got.strip() == expected.strip()
               for got, expected in zip(lines, suggestions))


def test_pull_obsolete(test_project, tmpdir):
    url = test_project.owner_basic_auth_url
    repo_path = tmpdir / 'repo'
    repo = prepare_simple_repo(test_project, repo_path)
    obsol_sha = repo.node('zetop')

    (repo_path / 'foo1').write('amended')
    repo.hg('amend', '-m', "Amended")

    repo.hg('push')

    clone = LocalRepo.clone(url, tmpdir.join('repo2'))
    nodes = [ext.node for ext in clone.changeset_extracts(['node'])[1]]
    assert obsol_sha not in nodes

    clone.hg('pull', '--remote-hidden', '-r', obsol_sha)
    assert clone.hg('log', '--hidden', '-r', obsol_sha,
                    '-T', '{desc}') == "Commit 1"
