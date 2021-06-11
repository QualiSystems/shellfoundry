# !/usr/bin/python
# -*- coding: utf-8 -*-

from io import open

import yaml

from shellfoundry.utilities.config_reader import INSTALL
from shellfoundry.utilities.modifiers.configuration.aggregated_modifiers import (
    AggregatedModifiers,
)


class ConfigContext(object):
    def __init__(self, config_file_path):
        self.config_file_path = config_file_path
        self.modifier = AggregatedModifiers()

    def try_save(self, key, value):
        try:
            with open(self.config_file_path, mode="r+", encoding="utf8") as stream:
                data = yaml.safe_load(stream) or {INSTALL: {}}
                data[INSTALL][key] = self._modify(key, value)
                stream.seek(0)
                stream.truncate()
                yaml.safe_dump(data, stream=stream, default_flow_style=False)
            return True
        except Exception:
            return False

    def try_delete(self, key):
        try:
            with open(self.config_file_path, mode="r+", encoding="utf8") as stream:
                data = yaml.safe_load(stream)
                del data[INSTALL][key]  # handle cases that INSTALL does not exists
                stream.seek(0)
                stream.truncate()
                yaml.safe_dump(data, stream=stream, default_flow_style=False)
            return True
        except Exception:
            return False

    def _modify(self, key, value):
        return self.modifier.modify(key, value)
