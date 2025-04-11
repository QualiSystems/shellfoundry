from __future__ import annotations

import os
import re
from typing import Sequence

import ruamel.yaml as yaml
from attrs import define, field

from shellfoundry.constants import (
    TEMPLATE_PROPERTY,
    TEMPLATE_VERSION,
    TOSCA_META_LOCATION,
)
from shellfoundry.exceptions import YmlFieldMissingException


@define
class DefinitionModification:
    shell_path: str
    entry_definition: str = field(init=False)

    def __attrs_post_init__(self):
        self.entry_definition = os.path.join(
            self.shell_path, self._find_entry_definition()
        )

    def edit_definition(self, conf_field: str, value: str) -> None:
        """Modify shell-definition.yaml.

        Parameters:
            conf_field: field name to modify
            value: new value to update
        """
        self._edit_yaml(self.entry_definition, conf_field, value)

    def edit_tosca_meta(self, conf_field: str, value: str) -> None:
        """Edit TOSCA.meta file."""
        with open(
            os.path.join(self.shell_path, TOSCA_META_LOCATION), encoding="utf8"
        ) as tosca_file:
            is_changed = False
            tosca_data = []
            for line in tosca_file:
                if conf_field in line:
                    line = re.sub(r":\s+.*", f": {value}", line)
                    is_changed = True
                tosca_data.append(line)

        if not is_changed:
            tosca_data.append(f"\n{conf_field}: {value}")

        with open(
            os.path.join(self.shell_path, TOSCA_META_LOCATION), "w", encoding="utf8"
        ) as tosca_file:
            tosca_file.writelines(tosca_data)

    def add_field_to_definition(
        self, conf_field: str, value: str | None = None, overwrite: bool = False
    ) -> None:
        """Add new field to shell-definition.yaml.

        Parameters:
            conf_field: field name to add
            value: value to add
            overwrite: overwrite value if it already exists
        """
        try:
            if overwrite:
                self.edit_definition(conf_field=conf_field, value=value)
        except YmlFieldMissingException:
            value = value or self._get_value_from_definition(TEMPLATE_VERSION)
            yaml_parser = yaml.YAML()
            loaded = self._load_yaml(
                yaml_parser=yaml_parser, yaml_file=self.entry_definition
            )

            section, field_name = conf_field.split("/", 1)
            loaded[section].update({field_name: value})
            self._edit_file(
                yaml_file=self.entry_definition, yaml_parser=yaml_parser, data=loaded
            )

    def add_properties(self, attribute_names: Sequence[str]) -> None:
        """Add property to shell-definition.yaml file.

        Parameter:
            fields: sequence of properties name that will be added
        """
        results = list(map(self._add_property, attribute_names))

        for item in zip(attribute_names, results):
            self._comment_attribute(*item)

    def get_artifacts_files(
        self, artifact_name_list: Sequence[str]
    ) -> dict[str, str] | None:
        yaml_parser = yaml.YAML()
        shell_definition = self._load_yaml(yaml_parser, self.entry_definition)

        for node_type in list(shell_definition["node_types"].values()):
            if "artifacts" not in node_type:
                continue

            result = {}
            for artifact_name, artifact in node_type["artifacts"].items():
                if artifact_name in artifact_name_list:
                    result.update({artifact_name: artifact["file"]})

            return result

    def _find_entry_definition(self) -> str:
        with open(os.path.join(self.shell_path, TOSCA_META_LOCATION)) as tosca_file:
            entry_definition = dict(
                list(map(str.strip, str(line).split(":", 1))) for line in tosca_file
            )["Entry-Definitions"]

            return entry_definition

    @staticmethod
    def _load_yaml(yaml_parser: yaml.YAML, yaml_file: str):
        with open(yaml_file, encoding="utf8") as stream:
            try:
                yaml_parser.indent(offset=2)
                return yaml_parser.load(stream=stream)
            except yaml.YAMLError as exc:
                print(exc)  # noqa: T001

    def _edit_yaml(self, yaml_file: str, conf_field: str, value: str) -> None:
        yaml_parser = yaml.YAML()
        loaded = self._load_yaml(yaml_parser=yaml_parser, yaml_file=yaml_file)

        field_name = conf_field.split("/")[-1]
        self._get_inner_dict_recursively(loaded, conf_field)[field_name] = value

        self._edit_file(yaml_file=yaml_file, yaml_parser=yaml_parser, data=loaded)

    @staticmethod
    def _edit_file(yaml_file: str, yaml_parser: yaml.YAML, data: str) -> None:
        with open(yaml_file, "wb") as f:
            yaml_parser.dump(data, stream=f)

    def _get_inner_dict_recursively(self, dic: dict, field_name: str) -> dict[str, str]:
        split = field_name.split("/", 1)
        i = dic.get(split[0])
        if not i:
            raise YmlFieldMissingException("Field does not exists")
        if not isinstance(i, dict) and len(split) == 1:
            return dic

        return self._get_inner_dict_recursively(i, split[1])

    def _get_value_from_definition(self, conf_field: str) -> str:
        yaml_parser = yaml.YAML()
        loaded = self._load_yaml(yaml_parser, self.entry_definition)

        field_name = conf_field.split("/")[-1]
        value = self._get_inner_dict_recursively(loaded, conf_field)[field_name]
        return value

    def _add_property(self, attribute_name: str) -> bool:
        """Add property to shell-definition.yaml file."""
        yaml_parser = yaml.YAML()
        loaded = self._load_yaml(yaml_parser, self.entry_definition)

        nodes = loaded.get("node_types")

        is_last = False
        if nodes:
            for key, value in nodes.items():
                if key.startswith("vendor."):
                    properties_data = value.get("properties", {})
                    if properties_data:
                        properties_data.update({attribute_name: TEMPLATE_PROPERTY})
                        is_last = False
                    else:
                        value.insert(
                            1, "properties", {attribute_name: TEMPLATE_PROPERTY}
                        )
                        is_last = True
                    break

            self._edit_file(
                yaml_file=self.entry_definition, yaml_parser=yaml_parser, data=loaded
            )

        return is_last

    def _comment_attribute(self, attribute_name: str, is_last: bool = False) -> None:
        """Comment attribute in shell-definition.yaml file."""
        spaces = None
        need_comment = False
        lines = []
        with open(self.entry_definition, encoding="utf8") as f:
            for line in f:
                stripped = line.lstrip(" ")
                if stripped.startswith(f"{attribute_name}:"):
                    if is_last:
                        lines[-1] = f"# {lines[-1]}"
                    spaces = len(line) - len(stripped)
                    need_comment = True
                    lines.append(f"# {line}")
                    continue

                if need_comment and spaces and (len(line) - len(stripped)) > spaces:
                    lines.append(f"# {line}")
                    continue

                need_comment = False
                lines.append(line)

        with open(self.entry_definition, "w", encoding="utf8") as f:
            f.writelines(lines)
