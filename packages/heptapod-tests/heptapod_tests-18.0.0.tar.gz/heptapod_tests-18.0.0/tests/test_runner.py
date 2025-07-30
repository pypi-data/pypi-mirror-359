from io import BytesIO
import re
from urllib.parse import urlparse
from zipfile import ZipFile

from selenium.webdriver.common.by import By

from . import suitable
from heptapod_tests.hg import LocalRepo
from heptapod_tests.runner import (
    job_variables,
    Runner,
)
from heptapod_tests.selenium import (
    wait_could_click,
)

from . import needs


def test_register_grab_job(test_project, tmpdir):
    test_project.only_specific_runners()
    runner = Runner.api_register(test_project, 'test_register')

    # registration consistency
    resp = runner.api_get()

    assert resp.status_code == 200
    as_json = resp.json()

    assert [p['id'] for p in as_json['projects']] == [test_project.id]
    assert as_json['is_shared'] is False
    assert as_json['active'] is True

    # no job yet
    assert runner.request_job() is None

    # push something and grab a job
    repo_path = tmpdir.join('repo1')
    repo = LocalRepo.init(repo_path)
    repo_path.join('foo').write('foo0')
    # let's not depend on auto-devops
    repo.init_gitlab_ci(message="With .gitlab-ci.yml")
    repo.hg('push', '-r', ".", '--publish', test_project.owner_basic_auth_url)
    node = repo.node('.')

    job = runner.wait_assert_one_job()

    vcs = job['git_info']
    assert vcs['hgsha'] == node
    assert vcs['ref'] == 'branch/default'
    assert vcs['ref_type'] == 'branch'
    assert vcs['repo_type'] == 'hg'

    variables = job_variables(job)
    for key, value in (('CI_COMMIT_HG_SHA', node),
                       ('CI_COMMIT_HG_SHORT_SHA', node[:12]),
                       ('CI_COMMIT_HG_BRANCH', 'default'),
                       ):
        assert variables[key] == value

    # the provided URL allows to clone, even though the project is private,
    # once the host/port are fixed to match the ones used in the test run
    # (and not, e.g., the external url setting, which is often different in
    # container context).
    heptapod_netloc = urlparse(runner.heptapod.url).netloc
    repo_url = re.sub(r'@(.*?)/', '@' + heptapod_netloc + '/', vcs['repo_url'])
    clone = LocalRepo.clone(repo_url, tmpdir.join('clone'))
    log = clone.hg('log', '-T', '{desc}\n')
    assert log.splitlines() == ['With .gitlab-ci.yml']

    runner.api_delete()
    resp = runner.api_get()
    assert resp.status_code == 404


@suitable.prod_server
def test_pipeline_pages_artifacts(test_project, tmpdir):
    with Runner.api_register(test_project, 'test_register') as runner:
        test_project.only_specific_runners()
        # push something and grab a job
        repo_path = tmpdir.join('repo1')
        repo = LocalRepo.init(repo_path)
        repo_path.join('foo').write('foo0')
        # let's not depend on auto-devops
        repo.init_gitlab_ci(message="With .gitlab-ci.yml")
        repo.hg('push', '-r', ".", '--publish',
                test_project.owner_basic_auth_url)

        job = runner.wait_assert_one_job()

        zip_path = tmpdir / 'artifacts.zip'
        with ZipFile(zip_path, 'w') as zf:
            zf.writestr('report.txt', b'artifact content')
        with zip_path.open('rb') as zfobj:
            runner.upload_artifact(job, zfobj)

        artif_fname, artif_body = test_project.get_job_artifacts(job)
        assert artif_fname in ('artifacts.zip', 'S3 content hash')
        with ZipFile(BytesIO(artif_body), 'r') as zf:
            with zf.open('report.txt') as innerf:
                assert innerf.read() == b'artifact content'

        # find the pipeline id in job payload
        job_vars = job_variables(job)
        pipeline_id = int(job_vars['CI_PIPELINE_ID'])

        # visit pipeline list and page
        webdriver = test_project.owner_webdriver
        webdriver.get(test_project.url + '/-/pipelines')

        # The Selenium webdriver is small enough to be considered mobile
        # Because of that, the column with pipeline IDs is not displayed
        # (even if the element is there, it is empty)
        pipeline_url = test_project.url + '/-/pipelines/%s' % pipeline_id

        wait_could_click(webdriver, By.XPATH, '//a[@data-testid="ci-icon"]')

        assert webdriver.current_url == pipeline_url

        assert '(500)' not in webdriver.title
        assert '(503)' not in webdriver.title


@suitable.prod_server
@needs.real_runner
def test_with_real_runner(test_project_with_real_runner, tmpdir):
    test_project = test_project_with_real_runner

    repo_path = tmpdir.join('repo1')
    repo = LocalRepo.init(repo_path)
    repo_path.join('foo').write('foo0')
    repo.hg('commit', '-Am', "Commit foo")
    repo.init_gitlab_ci(message="With .gitlab-ci.yml")
    hgsha = repo.node('.')
    repo.hg('push', '-r', ".", '--publish',
            test_project.owner_basic_auth_url)
    jobs = test_project.wait_assert_jobs_for_commit(hgsha)
    assert len(jobs) == 1
    job_id = jobs[0]['id']
    job = test_project.wait_assert_job(job_id,
                                       lambda j: j.get('finished_at'),
                                       timeout_factor=6)
    assert job['status'] == 'success'
