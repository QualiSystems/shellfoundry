#!/usr/bin/python
# -*- coding: utf-8 -*-
import json
import os
import re
from collections import OrderedDict, defaultdict
from io import open
from threading import RLock, Thread

import click
import requests
import yaml
from pkg_resources import parse_version

try:
    from pkg_resources._vendor.packaging.version import Version
except ImportError:
    from packaging.version import Version

from .filters import CompositeFilter

from shellfoundry.models.shell_template import ShellTemplate
from shellfoundry.utilities import GEN_TWO, SEPARATOR
from shellfoundry.utilities.constants import (
    SERVER_VERSION_KEY,
    TEMPLATE_INFO_FILE,
    TEMPLATES_YML,
)

REQUEST_TIMEOUT = 15


class TemplateRetriever(object):
    NAME_PLACEHOLDER = "name"

    def get_templates(self, **kwargs):
        """Get templates.

        :return: Dictionary of shellfoundry.ShellTemplate
        """
        alternative_path = kwargs.get("alternative", None)
        template_location = kwargs.get("template_location", None)
        standards = kwargs.get("standards", {})

        if alternative_path:
            response = self._get_templates_from_path(alternative_path)
            config = yaml.safe_load(response)
        elif template_location:
            config = self._get_local_templates(template_location=template_location)
        else:
            response = self._get_templates_from_github()
            config = yaml.safe_load(response)

        if not config or "templates" not in config:
            return {}

        templatesdic = defaultdict(list)
        for template in config["templates"]:

            if template["repository"]:  # Online templates
                standard_version = {}
            else:
                standard_version = template["standard_version"]

            templatesdic[template["name"]].append(
                ShellTemplate(
                    name=template["name"],
                    description=template["description"],
                    repository=template["repository"],
                    min_cs_ver=template["min_cs_ver"],
                    standard=self._get_standard_out_of_name(template["name"]),
                    standard_version=standard_version,
                    params=template["params"],
                )
            )

        return self._filter_by_standards(templatesdic, standards)

    @staticmethod
    def _get_templates_from_github():
        """Get templates data from GitHub."""
        session = requests.Session()
        session.mount("https://", requests.adapters.HTTPAdapter(max_retries=5))
        return session.get(TEMPLATES_YML, timeout=REQUEST_TIMEOUT).text

    @staticmethod
    def _get_templates_from_path(alternative_path):
        """Get templates data from local file."""
        with open(alternative_path, mode="r", encoding="utf8") as stream:
            response = stream.read()
        return response

    def _get_local_templates(self, template_location):
        """Get templates from local storage."""
        if not template_location or not os.path.exists(template_location):
            raise click.ClickException("Local template location empty or doesn't exist")
        else:
            templ_info = []
            for root, directories, filenames in os.walk(template_location):
                for filename in filenames:
                    if filename == TEMPLATE_INFO_FILE:
                        full_path = os.path.join(root, filename)

                        with open(full_path, mode="r", encoding="utf8") as f:
                            templ_data = json.load(f)

                        if GEN_TWO in templ_data.get("template_name", "Undefined"):
                            standard_version = self._get_standard_version_from_template(
                                root
                            )
                        else:
                            standard_version = templ_data.get(
                                "version", templ_data.get("shell_version", "0.0.1")
                            )

                        templ_info.append(
                            {
                                "name": templ_data.get("template_name", "Undefined"),
                                "description": templ_data.get(
                                    "template_descr", "Undefined"
                                ),
                                "min_cs_ver": templ_data.get(
                                    SERVER_VERSION_KEY, "Undefined"
                                ),
                                "repository": "",
                                "standard_version": {
                                    standard_version: {
                                        "repo": root,
                                        "min_cs_ver": templ_data.get(
                                            SERVER_VERSION_KEY, "Undefined"
                                        ),
                                    }
                                },
                                "params": {
                                    "project_name": templ_data.get(
                                        "project_name", None
                                    ),
                                    "family_name": templ_data.get("family_name", None),
                                },
                            }
                        )

            if templ_info:
                templates = {
                    "templates": sorted(
                        templ_info,
                        key=lambda data: list(data["standard_version"].keys())[0],
                    )
                }
            else:
                templates = None

        return templates

    @staticmethod
    def _get_standard_version_from_template(template_location):
        """Get standard version from template shell-definition file."""
        for root, directories, filenames in os.walk(template_location):
            for filename in filenames:
                if filename == "shell-definition.yaml":
                    with open(
                        os.path.join(root, "shell-definition.yaml"), encoding="utf8"
                    ) as stream:
                        match = re.search(
                            r"cloudshell_standard:\s*cloudshell_(?P<name>\S+)_standard_(?P<version>\S+)\.\w+$",  # noqa: E501
                            stream.read(),
                            re.MULTILINE,
                        )
                        if match:
                            return str(match.groupdict()["version"].replace("_", "."))

    @staticmethod
    def _get_standard_out_of_name(template_name, default=None):
        type_index = 0
        standard_index = 1
        template = template_name.split(SEPARATOR)
        if template[type_index] != GEN_TWO:
            return default
        return template[standard_index]

    @staticmethod
    def _filter_by_standards(templates, standards):
        """Filter templates by available on CloudShell Standards.

        :type templates collections.defaultdict(list)
        :type standards dict
        :return:
        """
        if not standards:
            return OrderedDict(sorted(templates.items()))

        global filtered_templates
        filtered_templates = defaultdict(list)

        threads = []
        lock = RLock()

        for template_name, templates_list in templates.items():
            template_thread = Thread(
                target=TemplateRetriever._filter_in_threads,
                args=(template_name, templates_list, standards, lock),
            )
            threads.append(template_thread)

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        return OrderedDict(sorted(filtered_templates.items()))

    @staticmethod
    def _filter_in_threads(template_name, templates_list, standards, lock):
        clear_template_name = TemplateRetriever._get_standard_out_of_name(template_name)
        if clear_template_name is None:
            for template in templates_list:
                lock.acquire()
                filtered_templates[template_name].append(template)
                lock.release()
        elif clear_template_name in list(standards.keys()):
            for template in templates_list:
                if (
                    not template.standard_version
                    or list(template.standard_version.keys())[0]
                    in standards[clear_template_name]
                ):
                    if template.repository:
                        template.min_cs_ver = (
                            TemplateRetriever._get_min_cs_version(
                                repository=template.repository,
                                standard_name=template.standard,
                                standards=standards,
                            )
                            or template.min_cs_ver
                        )
                    lock.acquire()
                    filtered_templates[template_name].append(template)
                    lock.release()

    @staticmethod
    def _get_min_cs_version(repository, standard_name, standards, branch=None):
        """Get minimal CloudShell Server Version available for provided template."""
        if not branch:
            branch = str(
                min(list(map(parse_version, standards[standard_name])))
            )  # determine minimal standard version
        repository = repository.replace("https://github.com", "https://raw.github.com")
        url = "/".join([repository, str(branch), "cookiecutter.json"])

        session = requests.Session()
        session.mount("https://", requests.adapters.HTTPAdapter(max_retries=5))
        responce = session.get(url, timeout=REQUEST_TIMEOUT)

        if responce.status_code == requests.codes.ok:
            return responce.json().get(SERVER_VERSION_KEY, None)
        else:
            return

    def get_repo_branches(self, repository, github_login=None, github_password=None):
        """Get all available branches for provided repository."""
        if repository.endswith("/"):
            repository = repository[:-1]
        request = "{}/branches".format(
            repository.replace("https://github.com", "https://api.github.com/repos")
        )

        session = requests.Session()
        if github_login and github_password:
            session.auth = (github_login, github_password)
        session.mount("https://", requests.adapters.HTTPAdapter(max_retries=5))
        response = session.get(request, timeout=REQUEST_TIMEOUT)

        response.raise_for_status()

        branches = [item[self.NAME_PLACEHOLDER] for item in response.json()]

        repo_branches = []
        for item in branches:
            if item == "master":
                repo_branches.append(item)
            elif isinstance(parse_version(item), Version):  # only numeric version
                repo_branches.append(parse_version(item))

        repo_branches.reverse()

        return repo_branches

    def get_latest_template(
        self, repo, version, github_login=None, github_password=None
    ):
        """Get latest template version based on CloudShell version."""
        for branch in self.get_repo_branches(repo, github_login, github_password):
            cs_version = self._get_min_cs_version(
                repository=repo, standard_name=None, standards=None, branch=branch
            )

            if cs_version:
                try:
                    if parse_version(version) >= parse_version(cs_version):
                        return str(branch)
                except Exception:
                    pass


class FilteredTemplateRetriever(object):
    def __init__(self, template_type, template_retriever=None):
        self.template_retriever = template_retriever or TemplateRetriever()
        self.filter = CompositeFilter(template_type).filter

    def get_templates(self, **kwargs):
        templates = self.template_retriever.get_templates(**kwargs)
        return OrderedDict((k, v) for k, v in templates.items() if self.filter(k))
