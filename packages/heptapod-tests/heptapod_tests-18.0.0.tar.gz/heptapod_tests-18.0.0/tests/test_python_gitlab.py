"""Tests involving the python-gitlab API client library."""

from .test_push import prepare_simple_repo
from heptapod_tests.git import LocalRepo as GitRepo


def test_python_gitlab_hg_project(test_project, tmpdir):
    proj = test_project
    api_client = proj.owner_user.python_gitlab_client
    gl_proj = api_client.projects.get(proj.id)
    vcs_type = 'hg' if proj.hg_native else 'hg_git'
    assert gl_proj.vcs_type == vcs_type

    repo = prepare_simple_repo(proj, tmpdir / 'repo')
    topic_hg_shas = dict(repo.changeset_extracts(('topic', 'node'))[1])

    for topic, gl_branch_name in (('', 'branch/default'),
                                  ('zetop', 'topic/default/zetop')):
        gl_commit = gl_proj.branches.get(gl_branch_name).commit
        hg_sha = topic_hg_shas[topic]
        assert gl_commit['hg_id'] == hg_sha
        assert gl_commit['short_hg_id'] == hg_sha[:12]


def test_python_gitlab_git_project(git_project, tmpdir):
    proj = git_project
    api_client = proj.owner_user.python_gitlab_client
    gl_proj = api_client.projects.get(proj.id)
    assert gl_proj.vcs_type == 'git'

    ssh_cmd, ssh_url = proj.owner_ssh_params

    repo_path = tmpdir / 'repo.git'
    repo = GitRepo.init(repo_path, default_url=ssh_url)
    repo_path.join('foo').write("Hey this is in Git!\n")
    repo.git('add', 'foo')
    repo.git('commit', '-m', 'Commit 0')
    repo.git('push', '--set-upstream', 'origin', 'master', ssh_cmd=ssh_cmd)

    gl_commit = gl_proj.branches.get('master').commit
    assert 'hg_id' not in gl_commit
    assert 'short_hg_id' not in gl_commit
