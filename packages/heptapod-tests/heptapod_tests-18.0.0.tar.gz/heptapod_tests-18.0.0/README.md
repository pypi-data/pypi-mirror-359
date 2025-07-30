# Heptapod automated functional tests

This source tree is both a library to write functional tests involving
Heptapod and the standard set of functional tests of Heptapod itself.

Caveats:

- Usage as a library is totally undocumented at this point.
- The distribution on pypi.org does not contain the tests of Heptapod
  itself. In other words, it contains the library part only.
- This README is mostly about the tests of Heptapod itself.


WARNING: to test production instances, use the dedicated mode exclusively. Other
modes assume that you are ready to **throw all data away** after the test
run, and hence are suitable at most for preflight full testing of a fresh
production instance.

## Installation

### Client-side install

#### Mercurial

The tests need a working `hg` executable, available on `$PATH`, with the
following extensions available:

- evolve and topic: [hg-evolve](https://pypi.org/project/hg-evolve) ≥ 9.3.0
- configexpress: [hg-configexpress](https://pypi.org/project/hg-configexpress)

#### Test harness (Selenium)

- tox: `pip install --user tox`
- [ChromeDriver](https://sites.google.com/a/chromium.org/chromedriver/home)

  For direct installation on the system running the tests:

  + Fedora 29 to 33: `dnf install chromedriver`
  + Debian 9 to 10, Ubuntu < 20.04: `apt install chromium-driver`
  + Ubuntu ≥ 20.04: the `chromium-driver` package actually installs a snap,
    which can be problematic in some environments. See how it is done in the
    `docker-inside` job of our [CI pipelines](.gitlab-ci.yml).

  Another option is to use a Selenium RemoteWebDriver, which proxies the
  actual web browsing through a dedicated system. Selenium provides the
  `selenium/standalone-chrome` Docker image for these purposes.

Note: on some systems, it happens that another Chrome executable is
found, usually on a more recent version, which can cause compatiility
concerns with the chromedriver version. This is more prone to happen with
chromedriver from a distribution, because it is more likely that it'd be
slightly outdated. In that case, since `chromedriver`
looks for Chrome as `/usr/bin/google-chrome` very early, it is possible
to solve the problem by creating a symlink pointing to the consistent
Chrome or Chromiium version.

All further dependencies will be installed by the first run.

### Heptapod server requirements

These tests can work against Heptapod servers provided either as

- (default) local Docker containers manageable by the system user running the
  tests, or
- installed from source and being run by the same user as the tests, or
- completely remote, skipping some of the tests, or
- production, relying on users with at most ownership of a dedicated projects
  group, and running a subset of suitable tests.

Except in production server mode, the Gitlab root password
will be initialized by the first test to run.
The tests will fail if the Gitlab root password is already set
and does not match the expected one.



### Default Docker setup

In the Docker case, the expected container name is by default `heptapod`.

By default, the tests expect to be running on the Docker host, and that the
container can initiate TCP connections to the host, identified as the main
IPv4 gateway of the container. Don't forget to *allow incoming TCP connections
from the container in your firewall*, if you have one. You can also pass a
reachable address explicitely with `--heptapod-reverse-call-host` or disable
such tests by passing an empty string as address.

The container HTTP and SSH ports must be forwarded by default to `heptapod:81`
and `heptapod:2022`. This is usually done by making the `heptapod` host name
resolve to a loopback IP address, such as 127.0.0.2, and forwarding the
container ports like this:

```
docker run --publish 127.0.0.2:2022:22 --publish 127.0.0.2:81:22
```

Using a dedicated host name and IP address helps preventing confusion in
the user's `.ssh/known_hosts` file.

## Running the tests

`tox` is the executable launching the tests. It is also responsible to
setup Python libraries used in the tests. The tests themselves are
written with [pytest](https://docs.pytest.org).

All `tox` commands have to be run from the root of this repository.

It is possible to pass down options to the underlying `pytest` command:

```
    tox -- --heptapod-url URL -k push_basic
```

All Heptapod specific options take the `--heptapod-some-option` form. For
the full list, do

```
   tox -- --help
```

### Common network options

These are available in all cases

- `--heptapod-url` (default `http://heptapod:81`): HTTP URL of the tested
  Heptapod instance. It must use a resolvable host *name*, not an IP address.
  It does not have to be resolved through DNS, an `/etc/host` entry pointing
  to the loopback interface is fine.
- `--heptapod-ssh-port` (default 2022): SSH port of the tested Heptapod
  instance. The same host name will be used as for HTTP. If the host name
  resolves to the loopback interface, it is advised to tie it to a dedicated
  address, such  as `127.0.0.2`, to minimize risks with your SSH
  `known_hosts` file.
- `--heptapod-reverse-call-host`: address that the Heptapod server can use
  to reach the system running theses tests (necessary to test outbound
  connections, such as web hooks).
- `--heptapod-root-password` (default `5iveL!fe`). The password to use and maybe
  set for the `root` user. The default value is the same as with the GitLab
  Development Kit (GDK).

### Running the tests concurrently

Use the `---tests-per-worker` option only.

Do *NOT* use the `--workers` option: it would setup the `Heptapod` session
fixture several times, leading to problems with GitLab user tokens and other
shared data that are session-local.

### Testing a Docker container

Being the default, this is the simplest. If you followed the default namings
and the current system user can managed Docker containers,
just running `tox` will launch the whole tests suite

Specific options:

- `--heptapod-container-name` (default `heptapod`)

### Testing a local install from source.

You will need to run the tests and the Heptapod server under the same user
and to pass some mandatory options:

Minimal example:

```
~/heptapod/heptapod-tests $ tox -- --heptapod-source-install\
    --heptapod--repositories-root ~/heptapod/gdk/repositories-root
```

### Testing a remote server
Mandatory reminder: **Never, ever run these tests on an
  Heptapod server if you're not prepared to throw all its data**

you'll have to provide the `--heptapod-remote` option, and probably be explicit
about all network options:

```
~/heptapod/heptapod-tests $ tox -- --heptapod-remote \
  --heptapod-ssh-port 22 \
  --heptapod-url https://heptapod.test \
  --heptapod-root-password SECRET
```

The root password option is listed because you probably don't want to have
an instance with the default root password available on the internet.

### Testing a production instance

*New on 2021-02-18*: see !80

To run the tests suitable for production instances, you will need first to
prepare:

- a projects group entirely dedicated to these functional tests
- a dedicated user that owns the dedicated group (more users will probably be
  needed in the future).

The production mode is activated by an explicit command-line option. Another
option is used to pass the dedicated user credentials.

Example:

```
~/heptapod/heptapod-tests $ tox -- --heptapod-prod-server \
    --heptapod-prod-group-owner-credentials ID:USERNAME:EMAIL:PASSWORD \
    --heptapod-url https://foss.heptapod.net \
    --heptapod-ssh-port 22 \
    --heptapod-ssh-user hg
```

where ID is the numeric user id, and USERNAME is the user login name
(e.g `testfonct`).

To launch tests on an instance tied to the Clever Cloud SSO,
use additionally the `--heptapod-clever-cloud-sso` option.


Remarks and safety:

- The user password must be fully operational: the functional tests won't
  take care of the finalization sequence that occurs at first login.
- Do not give the dedicated user any rights outside of the dedicated groups.
- It is advisable to block the dedicated user when not in use.
- Be prepared to receive email for Merge Requests on the dedicated user address.
  Arguably, this is part of the testing.


### Docker: choosing the version to test

The versions installed in the Docker image you're using are specified by the
[heptapod_revisions.json](https://dev.heptapod.net/heptapod/omnibus/blob/branch/heptapod/heptapod_docker/heptapod_revisions.json) file.

To test your local clone of heptapod/heptapod:

- mount your local `heptapod` clone in the container (assuming below it's seen
  as `/home/heptapod-rails` from the container)
- execute the following in the container:

  ```
  cd /var/opt/gitlab/embedded/service/gitlab-rails
  hg pull --config phases.publish=False /home/heptapod-rails
  hg up -r WISHED_REVISION
  gitlab-ctl restart unicorn
  ```

If you want to try changes to other components (e.g., `hg-git`), do something similar.
The paths can be seen in the Docker build logs, or you can read them in the [install script](https://dev.heptapod.net/heptapod/docker/blob/branch/default/heptapod/assets/install_heptapod.py)

## Adding new tests

### Branch and topics rules

The convention is that the tests in the default branch should pass against
the current `octobus/heptapod:latest` Docker image, so

* if you want to share a bug reproduction, please open a new topic
* even if a bug fix in heptapod has landed, please wait for the Docker push
  before publishing the corresponding tests
* tests can be published before a Heptapod new release, but please have the
  corresponding fixes landed and pushed to Docker Hub first.

If there is an active stable branch (e.g. `heptapod-0-6-stable` or similar),
then the tests of that branch must pass against the latest release version
corresponding to that branch. The same conclusions follow.
