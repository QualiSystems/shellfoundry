#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
import ssl

import pkg_resources

try:
    # Python 2.x version
    from xmlrpclib import ProtocolError, ServerProxy
except ImportError:
    # Python 3.x version
    from xmlrpc.client import ProtocolError, ServerProxy

try:
    from urllib import urlopen
except ImportError:
    from urllib.request import urlopen

try:
    from urllib.error import HTTPError, URLError
except ImportError:
    from urllib2 import HTTPError, URLError

from distutils.version import StrictVersion

from shellfoundry import PACKAGE_NAME
from shellfoundry.exceptions import ShellFoundryVersionException

GEN_ONE = "gen1"
GEN_TWO = "gen2"
LAYER_ONE = "layer1"
NO_FILTER = "all"
GEN_ONE_FILTER = "gen1"
GEN_TWO_FILTER = "gen2"
LAYER_ONE_FILTER = "layer-1"
SEPARATOR = "/"


class Index(object):
    def __init__(self, url):
        self.url = url


PyPI = Index("https://pypi.python.org/pypi/")


def get_installed_version(package_name):
    return pkg_resources.get_distribution(package_name).version


def is_index_version_greater_than_current():
    MAJOR_INDEX = 0

    installed, index = (
        StrictVersion(get_installed_version(PACKAGE_NAME)),
        StrictVersion(max_version_from_index()),
    )
    is_major_release = False

    is_greater_version = index > installed
    if (
        is_greater_version
        and get_index_of_biggest_component_between_two_versions(
            index.version, installed.version
        )
        == MAJOR_INDEX
    ):
        is_major_release = True

    return is_greater_version, is_major_release


def max_version_from_index():
    try:
        ctx = ssl.SSLContext(protocol=ssl.PROTOCOL_SSLv23)
        proxy = ServerProxy(PyPI.url, context=ctx)
        releases = proxy.package_releases(PACKAGE_NAME)
        max_version = max(releases)
        return max_version
    except ProtocolError as err:
        raise ShellFoundryVersionException(
            "Cannot retrieve latest shellfoundry version, "
            "are you offline? Error: {}".format(err)
        )
    except Exception as err:
        raise ShellFoundryVersionException(
            "Unexpected error during shellfoundry version check. "
            "Error: {}.".format(err)
        )


def latest_released_version():
    url = "https://pypi.org/pypi/{package_name}/json"
    try:
        package_info = json.load(urlopen(url.format(package_name=PACKAGE_NAME)))
        return package_info["info"]["version"]
    except (HTTPError, URLError) as err:
        raise ShellFoundryVersionException(
            "Cannot retrieve latest shellfoundry version, "
            "are you offline? Error: {}".format(err)
        )
    except Exception as err:
        raise ShellFoundryVersionException(
            "Unexpected error during shellfoundry version check. "
            "Error: {}.".format(err)
        )


def get_index_of_biggest_component_between_two_versions(v1, v2):
    for i in range(0, len(v1)):
        if v1[i] > v2[i]:
            return i
