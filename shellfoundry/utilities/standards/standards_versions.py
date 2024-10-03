#!/usr/bin/python
# -*- coding: utf-8 -*-

from pkg_resources import parse_version


class StandardVersionsFactory(object):
    def create(self, standards):
        return StandardVersions(standards)


class StandardVersions(object):
    def __init__(self, standards):
        if not standards:
            import os

            from shellfoundry import __file__ as sf_file

            raise Exception(
                "Standards list is empty. Please verify that {} exists".format(
                    os.path.join(os.path.dirname(sf_file), "data", "standards.json")
                )
            )

        self.standards = standards

    def get_latest_version(self, standard):
        standards = self.standards.get(standard, None)
        if standards is None:
            raise Exception("Failed to find latest version")

        latest_version = str(max(list(map(parse_version, standards))))
        if latest_version:
            return latest_version
