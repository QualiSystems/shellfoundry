#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
from io import open

from ..cloudshell_api import create_cloudshell_client

from shellfoundry.decorators.standards import standard_transformation


class Standards(object):
    @standard_transformation
    def fetch(self, **kwargs):
        alternative = kwargs.get("alternative", None)
        if not alternative:
            return self._fetch_from_cloudshell()
        return self._fetch_from_alternative_path(alternative)

    @staticmethod
    def _fetch_from_cloudshell():
        cs_client = create_cloudshell_client()
        try:
            return cs_client.get_installed_standards()
        except Exception:
            raise

    @staticmethod
    def _fetch_from_alternative_path(alternative_path):
        with open(alternative_path, mode="r", encoding="utf8") as stream:
            response = stream.read()
        return json.loads(response)
