from __future__ import annotations

import json
import os
import re
from collections import OrderedDict, defaultdict
from contextlib import suppress
from threading import RLock, Thread
from typing import Callable, ClassVar

import click
import requests
import yaml
from attrs import define, field
from packaging.version import Version, parse

from shellfoundry.constants import SERVER_VERSION_KEY, TEMPLATE_INFO_FILE, TEMPLATES_YML
from shellfoundry.exceptions import FatalError
from shellfoundry.models.shell_template import ShellTemplate
from shellfoundry.utilities.filters import GEN_TWO, SEPARATOR, CompositeFilter

REQUEST_TIMEOUT = 15


@define
class TemplateRetriever:
    NAME_PLACEHOLDER: ClassVar[str] = "name"

    def get_templates(self, **kwargs) -> dict[str, list[ShellTemplate]] | None:
        """Get templates."""
        templates = defaultdict(list)
        alternative_path = kwargs.get("alternative")
        template_location = kwargs.get("template_location")
        standards = kwargs.get("standards", {})

        if alternative_path:
            response = self._get_templates_from_path(alternative_path)
            config = yaml.safe_load(response)
        elif template_location:
            config = self._get_local_templates(template_location=template_location)
        else:
            response = self._get_templates_from_github()
            config = yaml.safe_load(response)

        if config and "templates" in config:
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
            templates = self._filter_by_standards(templatesdic, standards)

        return templates

    @staticmethod
    def _get_templates_from_github():
        """Get templates data from GitHub."""
        session = requests.Session()
        session.mount("https://", requests.adapters.HTTPAdapter(max_retries=5))
        return session.get(TEMPLATES_YML, timeout=REQUEST_TIMEOUT).text

    @staticmethod
    def _get_templates_from_path(alternative_path: str) -> str:
        """Get templates data from local file."""
        with open(alternative_path, encoding="utf8") as stream:
            response = stream.read()
        return response

    def _get_local_templates(
        self, template_location: str
    ) -> dict[str, list[dict[str, str | dict]]]:  # noqa: E501
        """Get templates from local storage."""
        if not template_location or not os.path.exists(template_location):
            raise click.ClickException("Local template location empty or doesn't exist")
        else:
            templ_info = []
            for root, directories, filenames in os.walk(template_location):
                for filename in filenames:
                    if filename == TEMPLATE_INFO_FILE:
                        full_path = os.path.join(root, filename)

                        with open(full_path, encoding="utf8") as f:
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
    def _get_standard_version_from_template(template_location: str) -> str | None:
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
    def _get_standard_out_of_name(
        template_name: str, default: str = None
    ) -> str | None:
        type_index = 0
        standard_index = 1
        template = template_name.split(SEPARATOR)
        if template[type_index] != GEN_TWO:
            return default
        return template[standard_index]

    @staticmethod
    def _filter_by_standards(
        templates: dict[str, list[ShellTemplate]], standards: dict[str, list[str]]
    ) -> dict[str, list[ShellTemplate]]:
        """Filter templates by available on CloudShell Standards."""
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
    def _filter_in_threads(
        template_name: str,
        templates_list: list[ShellTemplate],
        standards: dict[str, list[str]],
        lock: RLock,
    ) -> None:
        """Method for filter templates in Threads."""
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
    def _get_min_cs_version(
        repository: str,
        standard_name: str | None,
        standards: dict[str, list[str]] | None,
        branch: str | None = None,
    ) -> str | None:
        """Get minimal CloudShell Server Version available for provided template."""
        if not branch:
            if not standards or standard_name:
                raise FatalError(
                    "Error during CS version determination due to insufficient data."
                )
            branch = str(
                min(list(map(parse, standards[standard_name])))
            )  # determine minimal standard version
        repository = repository.replace("https://github.com", "https://raw.github.com")
        url = "/".join([repository, str(branch), "cookiecutter.json"])

        session = requests.Session()
        session.mount("https://", requests.adapters.HTTPAdapter(max_retries=5))
        response = session.get(url, timeout=REQUEST_TIMEOUT)

        if response.status_code == requests.codes.ok:
            return response.json().get(SERVER_VERSION_KEY)

    def get_repo_branches(
        self,
        repository: str,
        github_login: str | None = None,
        github_password: str | None = None,
    ) -> list[str]:
        """Get all available branches for provided repository."""
        if repository.endswith("/"):
            repository = repository[:-1]
        request = f"{repository.replace('https://github.com', 'https://api.github.com/repos')}/branches"  # noqa: E501

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
            elif isinstance(parse(item), Version):  # only numeric version
                repo_branches.append(parse(item))

        repo_branches.reverse()

        return repo_branches

    def get_latest_template(
        self,
        repo: str,
        version: str,
        github_login: str | None = None,
        github_password: str | None = None,
    ) -> str | None:
        """Get latest template version based on CloudShell version."""
        for branch in self.get_repo_branches(repo, github_login, github_password):
            cs_version = self._get_min_cs_version(
                repository=repo, standard_name=None, standards=None, branch=branch
            )

            if cs_version:
                with suppress(Exception):
                    if parse(version) >= parse(cs_version):
                        return str(branch)


@define
class FilteredTemplateRetriever:
    template_type: str | None
    template_retriever: TemplateRetriever = field(factory=TemplateRetriever)
    passes: Callable[[str], bool] = field(init=False)

    def __attrs_post_init__(self):
        self.passes = CompositeFilter(self.template_type).passes

    def get_templates(self, **kwargs):
        templates = self.template_retriever.get_templates(**kwargs)
        return OrderedDict((k, v) for k, v in templates.items() if self.passes(k))
