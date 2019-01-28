#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import re
import ruamel.yaml as yaml

from shellfoundry.utilities.constants import TOSCA_META_LOCATION, TEMPLATE_VERSION, TEMPLATE_PROPERTY

from shellfoundry.exceptions import YmlFieldMissingException


class DefinitionModification(object):
    def __init__(self, shell_path):
        self.shell_path = shell_path
        self.entry_definition = os.path.join(self.shell_path, self._find_entry_definition())

    def edit_definition(self, field, value):
        """ Modify shell-definition.yaml
        :params field str: field name to modify
        :params value str: new value to update
        """

        self._edit_yaml(self.entry_definition, field, value)

    def edit_tosca_meta(self, field, value):
        """  """

        with open(os.path.join(self.shell_path, TOSCA_META_LOCATION), "r") as tosca_file:
            is_changed = False
            tosca_data = []
            for line in tosca_file:
                if field in line:
                    line = re.sub(r":\s+.*", ": {}".format(value), line)
                    is_changed = True
                tosca_data.append(line)

        if not is_changed:
            tosca_data.append("\n{field}: {value}".format(field=field, value=value))

        with open(os.path.join(self.shell_path, TOSCA_META_LOCATION), "wb") as tosca_file:
            tosca_file.writelines(tosca_data)

    def add_field_to_definition(self, field, value=None, overwrite=False):
        """ Add new field to shell-definition.yaml
        :params field str: field name to add
        :params value str: value to add
        :params overwrite bool: overwrite value if it already exists
        """

        try:
            based_on_version = self._get_value_from_definition(field)
            if overwrite:
                self.edit_definition(field, value)
        except YmlFieldMissingException:
            value = value or self._get_value_from_definition(TEMPLATE_VERSION)
            yaml_parser = yaml.YAML()
            loaded = self._load_yaml(yaml_parser=yaml_parser, yaml_file=self.entry_definition)

            section, field_name = field.split("/", 1)
            loaded[section].update({field_name: value})
            self._edit_file(yaml_file=self.entry_definition, yaml_parser=yaml_parser, data=loaded)

    def add_properties(self, attribute_names):
        """ Add property to shell-definition.yaml file
        :params fields tuple/list: sequence of properties name that will be added
        """

        results = map(self._add_property, attribute_names)

        for item in zip(attribute_names, results):
            self._comment_attribute(*item)

    def get_artifacts_files(self, artifact_name_list):
        """  """
        yaml_parser = yaml.YAML()
        shell_definition = self._load_yaml(yaml_parser, self.entry_definition)

        for node_type in shell_definition["node_types"].values():
            if "artifacts" not in node_type:
                continue

            result = {}
            for artifact_name, artifact in node_type["artifacts"].iteritems():
                if artifact_name in artifact_name_list:
                    result.update({artifact_name: artifact["file"]})

            return result

    def _find_entry_definition(self):
        """  """

        with open(os.path.join(self.shell_path, TOSCA_META_LOCATION), "r") as tosca_file:
            entry_definition = dict(map(str.strip, line.split(":", 1)) for line in tosca_file)["Entry-Definitions"]

            return entry_definition

    def _load_yaml(self, yaml_parser, yaml_file):
        """  """

        with open(yaml_file) as stream:
            try:
                yaml_parser.indent(offset=2)
                return yaml_parser.load(stream=stream)
            except yaml.YAMLError as exc:
                print(exc)

    def _edit_yaml(self, yaml_file, field, value):
        """  """

        yaml_parser = yaml.YAML()
        loaded = self._load_yaml(yaml_parser=yaml_parser, yaml_file=yaml_file)

        field_name = field.split("/")[-1]
        self._get_inner_dict_recursively(loaded, field)[field_name] = value

        self._edit_file(yaml_file=yaml_file, yaml_parser=yaml_parser, data=loaded)

    def _edit_file(self, yaml_file, yaml_parser, data):
        with open(yaml_file, "wb") as f:
            yaml_parser.dump(data, stream=f)

    def _get_inner_dict_recursively(self, dic, field):
        """  """

        split = field.split("/", 1)
        i = dic.get(split[0])
        if not i:
            raise YmlFieldMissingException("Field does not exists")
        if not isinstance(i, dict) and len(split) == 1:
            return dic

        return self._get_inner_dict_recursively(i, split[1])

    def _get_value_from_definition(self, field):
        """  """

        yaml_parser = yaml.YAML()
        loaded = self._load_yaml(yaml_parser, self.entry_definition)

        field_name = field.split("/")[-1]
        value = self._get_inner_dict_recursively(loaded, field)[field_name]
        return value

    def _add_property(self, attribute_name):
        """ Add property to shell-definition.yaml file
        :params fields list: list of properties name that will be added
        """

        yaml_parser = yaml.YAML()
        loaded = self._load_yaml(yaml_parser, self.entry_definition)

        nodes = loaded.get("node_types")

        is_last = False
        if nodes:
            for key, value in nodes.iteritems():
                if key.startswith("vendor."):
                    properties_data = value.get("properties", {})
                    if properties_data:
                        properties_data.update({attribute_name: TEMPLATE_PROPERTY})
                        is_last = False
                    else:
                        value.insert(1, "properties", {attribute_name: TEMPLATE_PROPERTY})
                        is_last = True
                    break

            self._edit_file(yaml_file=self.entry_definition, yaml_parser=yaml_parser, data=loaded)

        return is_last

    def _comment_attribute(self, attribute_name, is_last=False):
        """ Comment attribute in shell-definishion.yaml file """

        spaces = None
        need_comment = False
        lines = []
        with open(self.entry_definition, "r") as f:
            for line in f:
                stripped = line.lstrip(' ')
                if stripped.startswith("{}:".format(attribute_name)):
                    if is_last:
                        lines[-1] = "# {}".format(lines[-1])
                    spaces = len(line) - len(stripped)
                    need_comment = True
                    lines.append("# {}".format(line))
                    continue

                if need_comment and spaces and (len(line) - len(stripped)) > spaces:
                    lines.append("# {}".format(line))
                    continue

                need_comment = False
                lines.append(line)

        with open(self.entry_definition, "w") as f:
            f.writelines(lines)
