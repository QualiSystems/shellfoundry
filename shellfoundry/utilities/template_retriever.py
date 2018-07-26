#!/usr/bin/python
# -*- coding: utf-8 -*-

import click
import os
import requests
import yaml
import json
import re

from collections import OrderedDict, defaultdict

from .filters import CompositeFilter
from shellfoundry.models.shell_template import ShellTemplate
from shellfoundry.utilities import GEN_TWO, SEPARATOR
from shellfoundry.utilities.constants import TEMPLATE_INFO_FILE

TEMPLATES_YML = 'https://raw.github.com/QualiSystems/shellfoundry/master/templates_v1.yml'


class TemplateRetriever(object):
    def get_templates(self, **kwargs):
        """
        :return: Dictionary of shellfoundry.ShellTemplate
        """

        alternative_path = kwargs.get('alternative', None)
        template_location = kwargs.get('template_location', None)
        standards = kwargs.get('standards', {})

        if alternative_path:
            response = self._get_templates_from_path(alternative_path)
            config = yaml.load(response)
        elif template_location:
            config = self._get_local_templates(template_location=template_location)
        else:
            response = self._get_templates_from_github()
            config = yaml.load(response)

        if not config or 'templates' not in config:
            return {}

        templatesdic = defaultdict(list)
        for template in config['templates']:

            if template["repository"]:  # Online templates
                standard_version = {}
            else:
                standard_version = template["standard_version"]

            templatesdic[template["name"]].append(ShellTemplate(name=template['name'],
                                                                description=template['description'],
                                                                repository=template['repository'],
                                                                min_cs_ver=template['min_cs_ver'],
                                                                standard=self._get_standard_out_of_name(template['name']),
                                                                standard_version=standard_version,
                                                                params=template['params']))

        return self._filter_by_standards(templatesdic, standards)

    @staticmethod
    def _get_templates_from_github():
        session = requests.Session()
        session.mount('https://', requests.adapters.HTTPAdapter(max_retries=5))
        return session.get(TEMPLATES_YML).text

    @staticmethod
    def _get_templates_from_path(alternative_path):
        with open(alternative_path, mode='r') as stream:
            response = stream.read()
        return response

    def _get_local_templates(self, template_location):
        """  """

        if not template_location or not os.path.exists(template_location):
            raise click.ClickException("Local template location empty or doesn't exist")
        else:
            templ_info = []
            for root, directories, filenames in os.walk(template_location):
                for filename in filenames:
                    if filename == TEMPLATE_INFO_FILE:
                        full_path = os.path.join(root, filename)
                        standard_version = self._get_standard_version_from_template(root)
                        with open(full_path, mode='r') as f:
                            templ_data = json.load(f)
                        templ_info.append({"name": templ_data.get("template_name", "Undefined"),
                                           "description": templ_data.get("template_descr", "Undefined"),
                                           "min_cs_ver": templ_data.get("server_version", "Undefined"),
                                           "repository": "",
                                           "standard_version": {standard_version: {"repo": root,
                                                                                   "min_cs_ver": templ_data.get(
                                                                                       "server_version", "Undefined")}},
                                           "params": {"project_name": templ_data.get("project_name", None),
                                                      "family_name": templ_data.get("family_name", None)}})

            if templ_info:
                templates = {"templates": templ_info}
            else:
                templates = None

        return templates

    @staticmethod
    def _get_standard_version_from_template(template_location):
        """  """

        for root, directories, filenames in os.walk(template_location):
            for filename in filenames:
                if filename == "shell-definition.yaml":
                    with open(os.path.join(root, "shell-definition.yaml")) as stream:
                        match = re.search(
                            r"cloudshell_standard:\s*cloudshell_(?P<name>\S+)_standard_(?P<version>\S+)\.\w+$",
                            stream.read(),
                            re.MULTILINE)
                        if match:
                            return str(match.groupdict()["version"].replace("_", "."))

    @staticmethod
    def _get_standard_out_of_name(template_name, default=None):
        """
        :type template_name str
        :return:
        """

        type_index = 0
        standard_index = 1
        template = template_name.split(SEPARATOR)
        if template[type_index] != GEN_TWO:
            return default
        return template[standard_index]

    @staticmethod
    def _filter_by_standards(templates, standards):
        """
        :type templates collections.defaultdict(list)
        :type standards dict
        :return:
        """
        if not standards:
            return OrderedDict(sorted(templates.iteritems()))

        filtered_templates = defaultdict(list)
        for template_name, templates_list in templates.iteritems():
            clear_template_name = TemplateRetriever._get_standard_out_of_name(template_name)
            if clear_template_name is None:
                for template in templates_list:
                    filtered_templates[template_name].append(template)
            elif clear_template_name in standards.keys():
                for template in templates_list:
                    if not template.standard_version or template.standard_version.keys()[0] in standards[clear_template_name]:
                        filtered_templates[template_name].append(template)

        return OrderedDict(sorted(filtered_templates.iteritems()))


class FilteredTemplateRetriever(object):
    def __init__(self, template_type, template_retriever=None):
        self.template_retriever = template_retriever or TemplateRetriever()
        self.filter = CompositeFilter(template_type).filter

    def get_templates(self, **kwargs):
        templates = self.template_retriever.get_templates(**kwargs)
        return OrderedDict((k, v) for k, v in templates.iteritems() if self.filter(k))
