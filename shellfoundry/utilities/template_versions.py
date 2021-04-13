#!/usr/bin/python
# -*- coding: utf-8 -*-

import requests

import shellfoundry.exceptions as exc

VERSIONS_URL = "https://api.github.com/repos/{}/{}/branches"
NAME_PLACEHOLDER = "name"


def is_version(vstr):
    from distutils.version import StrictVersion

    try:
        StrictVersion(vstr)
        return True
    except Exception:
        return False


class TemplateVersions(object):
    def __init__(self, url_user, url_repo):
        self.template_repo = [url_user, url_repo]

    def get_versions_of_template(self):
        """Get all versions (branches) of a given template.

        Raises HTTPError on request fail,
        NoVersionsHaveBeenFoundException when no versions have been found
        :return: List filled with version names (e.g. 1.0, 1.1, 2.0...)
        """
        response = requests.get(VERSIONS_URL.format(*self.template_repo))
        response.raise_for_status()

        branches = [d[NAME_PLACEHOLDER] for d in response.json()]
        branches.sort(reverse=True, key=lambda x: (is_version(x), x))
        if not self.has_versions(branches):
            raise exc.NoVersionsHaveBeenFoundException(
                "No versions have been found for this template"
            )
        return branches

    @staticmethod
    def has_versions(branches):
        first_branch = next(iter(branches or []), None)
        return first_branch is not None
