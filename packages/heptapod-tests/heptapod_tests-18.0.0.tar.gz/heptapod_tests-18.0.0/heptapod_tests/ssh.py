"""Utilities for dealing with SSH."""
import subprocess


def url_server_keys(url):
    """Return the server keys for URL in the `known_hosts` format.

    Does not support pure IPv6 hosts given by hostname, nor IPv6 address
    URLs such as `ssh://[::1]:22` (two different reasons for this).

    :param url: parsed URL
    """
    # netloc contains user and password (the later not expected for SSH)
    split = url.netloc.split('@', 1)
    if len(split) == 1:
        without_user = split[0]
    else:
        without_user = split[1]

    split = without_user.rsplit(':', 1)
    if len(split) == 1:
        host, port = split, 22
    else:
        host, port = split
    return subprocess.check_output(
        # GDK's SSH server is configured for IPv4 only,
        # and ssh-keyscan does not know how to fall back to IPv4
        # if there is an IPv6 resolution. On the other hand, pure IPv6
        # servers are quite uncommon.
        ('ssh-keyscan', '-4', '-p', str(port), host),
        stderr=subprocess.PIPE
    ).decode()
