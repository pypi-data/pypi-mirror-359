"""High level utilities to prepare test content."""
from heptapod_tests.git import LocalRepo as GitRepo
from heptapod_tests.hg import LocalRepo as HgRepo


def prepare_import_source_hg(project, tmpdir, tweak_hgrc=True):
    """Prepare given project to be the import source for tests.

    :return: LocalRepo object, external URL of project

    The external URL of a project is acceptable as an import source URL
    within the same instance. All URLs to the Docker container (file://, or
    http on an alternate port) would be rejected as forgery attempts.
    (see app/validators/importable_url_validator.rb in heptapod-rails)
    """
    if tweak_hgrc:
        project.api_hgrc_set(inherit=True,
                             allow_multiple_heads=True,
                             allow_bookmarks=True,
                             auto_publish='nothing')
    repo = HgRepo.init(tmpdir.join('import_src'),
                       default_url=project.owner_basic_auth_url)
    repo.path.join('kitten').write("A lion is stronger than a kitten\n")
    repo.hg('commit', '-Am', "Initial sentence")
    repo.path.join('horse').write("A lion is stronger than a horse\n")
    repo.hg('commit', '-Am', "Even a horse!")
    repo.hg('up', '0')
    repo.hg('topic', 'antelope')
    repo.path.join('antelope').write("A lion is stronger than an antelope\n")
    repo.hg('commit', '-Am', "Même une antilope !",
            '--user', 'Raphaël <raphael@heptapod.test>')
    repo.hg('push')

    project_external_url = project.api_get_field('http_url_to_repo')
    assert project_external_url is not None
    return repo, project_external_url


def prepare_import_source_git(project, tmpdir):
    repo_path = tmpdir.join('import_src')

    repo = GitRepo.init(repo_path, default_url=project.owner_basic_auth_url)
    repo_path.join('foo').write("Hey this is in Git!\n")
    repo.git('add', 'foo')
    repo.git('commit', '-m', 'Commit 0')
    repo.git('push', '--set-upstream', 'origin', 'master')

    project_external_url = project.api_get_field('http_url_to_repo')
    assert project_external_url is not None
    return repo, project_external_url
