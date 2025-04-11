from __future__ import annotations

import yaml
from attrs import define, field

from shellfoundry.utilities.config_reader import INSTALL
from shellfoundry.utilities.modifiers.configuration.aggregated_modifiers import (
    AggregatedModifiers,
)


@define
class ConfigContext:
    config_file_path: str
    modifier: AggregatedModifiers = field(init=False, factory=AggregatedModifiers)

    def try_save(self, key: str, value: str) -> bool:
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

    def try_delete(self, key: str) -> bool:
        try:
            with open(self.config_file_path, mode="r+", encoding="utf8") as stream:
                data = yaml.safe_load(stream)
                del data[INSTALL][key]  # handle cases that INSTALL does not exist
                stream.seek(0)
                stream.truncate()
                yaml.safe_dump(data, stream=stream, default_flow_style=False)
            return True
        except Exception:
            return False

    def _modify(self, key: str, value: str) -> str:
        return self.modifier.modify(key, value)
