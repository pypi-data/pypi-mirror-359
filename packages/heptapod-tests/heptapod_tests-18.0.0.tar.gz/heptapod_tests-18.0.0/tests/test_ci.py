"""Various tests involving CI/CD, not directly related to push nor MR support.
"""
from urllib import request
from urllib.parse import urlencode

from heptapod_tests import hg
from heptapod_tests.runner import job_variables


def test_trigger_token(test_project_with_runner, tmpdir):
    proj, runner = test_project_with_runner
    repo_path = tmpdir.join('repo1')
    repo = hg.LocalRepo.init(repo_path, default_url=proj.owner_basic_auth_url)
    repo.init_gitlab_ci()
    repo.hg('push', *hg.cli_pushvars({'ci.skip': True}))

    token = proj.api_create_pipeline_trigger_token()

    data = dict(token=token, ref='branch/default')
    data['variables[HPD_TESTS]'] = 'fooo'

    # using urllib directly instead of requests, to match current
    # investigations about issue encountered by a script of Tryton's
    req = request.Request(proj.api_url + '/trigger/pipeline',
                          data=urlencode(data).encode())
    with request.urlopen(req) as resp:
        assert resp.status == 201

    job = runner.wait_assert_one_job()
    job_vars = job_variables(job)
    assert job_vars['CI_PIPELINE_SOURCE'] == 'trigger'
    assert job_vars['HPD_TESTS'] == 'fooo'
