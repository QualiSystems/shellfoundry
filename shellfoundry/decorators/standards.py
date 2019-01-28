#!/usr/bin/python
# -*- coding: utf-8 -*-

from shellfoundry.utilities.standards.consts import STANDARD_NAME_KEY, VERSIONS_KEY


def standard_transformation(fetch):
    def wrapper(self, **kwargs):
        result = fetch(self, **kwargs)
        return {i[STANDARD_NAME_KEY].lower().lstrip('cloudshell').rstrip('standard').strip('_').replace('_', '-'):
                    i[VERSIONS_KEY] for i in result}
    return wrapper
