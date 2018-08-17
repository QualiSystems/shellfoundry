#!/usr/bin/python
# -*- coding: utf-8 -*-

import requests
import json
try:
    from pip.utils import get_installed_version
except ImportError:
    def get_installed_version(package_name):
        return __import__(package_name).__version__

from distutils.version import StrictVersion

from shellfoundry import PACKAGE_NAME
from shellfoundry.exceptions import ShellFoundryVersionException


GEN_ONE = 'gen1'
GEN_TWO = 'gen2'
LAYER_ONE = 'layer1'
NO_FILTER = 'all'
GEN_ONE_FILTER = 'gen1'
GEN_TWO_FILTER = 'gen2'
LAYER_ONE_FILTER = 'layer-1'
SEPARATOR = '/'


class Index(object):
    def __init__(self, url):
        self.url = url


PyPI = Index('https://pypi.python.org/pypi/')


def is_index_version_greater_than_current():
    MAJOR_INDEX = 0

    installed, index = (StrictVersion(get_installed_version(PACKAGE_NAME)), StrictVersion(max_version_from_index()))
    is_major_release = False

    is_greater_version = index > installed
    if is_greater_version and get_index_of_biggest_component_between_two_versions(index.version,
                                                                                  installed.version) == MAJOR_INDEX:
        is_major_release = True

    return is_greater_version, is_major_release


def max_version_from_index():
    try:
        url = 'https://pypi.org/pypi/{}/json'.format(PACKAGE_NAME)
        r = requests.get(url, stream=True)
        if r.status_code != requests.codes.ok:
            raise ShellFoundryVersionException("Cannot retrieve latest shellfoundry version, "
                                               "are you offline?")
        else:
            content = json.loads(r.content)
            max_version = content['info']['version']
            return max_version
    except Exception, err:
        raise ShellFoundryVersionException("Cannot retrieve latest shellfoundry version, "
                                           "are you offline? Error: {}".format(err.message))


def get_index_of_biggest_component_between_two_versions(v1, v2):
    for i in xrange(0, len(v1)):
        if v1[i] > v2[i]:
            return i
