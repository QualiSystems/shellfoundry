#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
import os
import re
from io import open

import click
from cloudshell.rest.exceptions import FeatureUnavailable
from pkg_resources import parse_version
from requests.exceptions import SSLError

from ..exceptions import FatalError

from shellfoundry import (
    ALTERNATIVE_STANDARDS_PATH,
    ALTERNATIVE_TEMPLATES_PATH,
    MASTER_BRANCH_NAME,
)
from shellfoundry.exceptions import VersionRequestException
from shellfoundry.utilities.config_reader import CloudShellConfigReader, Configuration
from shellfoundry.utilities.constants import TEMPLATE_INFO_FILE
from shellfoundry.utilities.cookiecutter_integration import CookiecutterTemplateCompiler
from shellfoundry.utilities.repository_downloader import RepositoryDownloader
from shellfoundry.utilities.standards import Standards, StandardVersionsFactory
from shellfoundry.utilities.temp_dir_context import TempDirContext
from shellfoundry.utilities.template_retriever import TemplateRetriever
from shellfoundry.utilities.template_versions import TemplateVersions
from shellfoundry.utilities.validations import ShellNameValidations


class NewCommandExecutor(object):
    LOCAL_TEMPLATE_URL_PREFIX = "local:"
    REMOTE_TEMPLATE_URL_PREFIX = "url:"
    L1_TEMPLATE = "layer-1-switch"

    def __init__(
        self,
        template_compiler=None,
        template_retriever=None,
        repository_downloader=None,
        standards=None,
        standard_versions=None,
        shell_name_validations=None,
    ):
        """Creates shell based on template and standards.

        :param CookiecutterTemplateCompiler template_compiler:
        :param TemplateRetriever template_retriever:
        :param RepositoryDownloader repository_downloader:
        :param Standards standards:
        :param StandardVersionsFactory standard_versions:
        :param ShellNameValidations shell_name_validations:
        """
        self.cloudshell_config_reader = Configuration(CloudShellConfigReader())
        self.template_retriever = template_retriever or TemplateRetriever()
        self.repository_downloader = repository_downloader or RepositoryDownloader()
        self.template_compiler = template_compiler or CookiecutterTemplateCompiler()
        self.standards = standards or Standards()
        self.standard_versions = standard_versions or StandardVersionsFactory()
        self.shell_name_validations = shell_name_validations or ShellNameValidations()

    def new(self, name, template, version=None, python_version="3"):
        """Create a new shell based on a template.

        :param str version: The desired version of the shell template to use
        :param str name: The name of the Shell
        :param str template: The name of the template to use
        :param str python_version: Python version
        """
        # Special handling for the case where the user runs 'shellfoundry .'
        # in such a case the '.' character is substituted for the shell name
        # and the content of the current folder is populated
        running_on_same_folder = False
        if name == os.path.curdir:
            name = os.path.split(os.getcwd())[1]
            running_on_same_folder = True

        if not self.shell_name_validations.validate_shell_name(name):
            raise click.BadParameter(
                "Shell name must begin with a letter "
                "and contain only alpha-numeric characters and spaces."
            )

        try:
            standards = self.standards.fetch()
        except FeatureUnavailable:
            standards = self.standards.fetch(alternative=ALTERNATIVE_STANDARDS_PATH)
        except Exception as err:
            raise click.ClickException(
                "Cannot retrieve standards list. Error: {}".format(err)
            )

        # Get template using direct url path. Ignore parameter in configuration file
        if self._is_direct_online_template(template):
            self._import_direct_online_template(
                name, running_on_same_folder, template, standards, python_version
            )
        # Get template using direct path. Ignore parameter in configuration file
        elif self._is_direct_local_template(template):
            self._import_local_template(
                name, running_on_same_folder, template, standards, python_version
            )
        # Get template from GitHub repository
        elif self.cloudshell_config_reader.read().online_mode.lower() == "true":
            self._import_online_template(
                name,
                running_on_same_folder,
                template,
                version,
                standards,
                python_version,
            )
        # Get template from location defined in shellfoundry configuration
        else:
            template = self._get_local_template_full_path(template, standards, version)
            self._import_local_template(
                name, running_on_same_folder, template, standards, python_version
            )

        if template == self.L1_TEMPLATE:
            click.secho("WARNING: L1 shells support python 2.7 only!", fg="yellow")

        click.echo("Created shell {0} based on template {1}".format(name, template))

    def _import_direct_online_template(
        self, name, running_on_same_folder, template, standards, python_version
    ):
        """Create shell based on template downloaded by the direct link."""
        template_url = self._remove_prefix(
            template, NewCommandExecutor.REMOTE_TEMPLATE_URL_PREFIX
        )
        with TempDirContext(name) as temp_dir:
            try:
                repo_path = self.repository_downloader.download_template(
                    temp_dir, template_url, branch=None, is_need_construct=False
                )
            except VersionRequestException:
                raise click.BadParameter(
                    "Failed to download template from provided direct link {}".format(
                        template_url
                    )
                )

            self._verify_template_standards_compatibility(
                template_path=repo_path, standards=standards
            )

            extra_content = self._get_template_params(repo_path=repo_path)

            self.template_compiler.compile_template(
                shell_name=name,
                template_path=repo_path,
                extra_context=extra_content,
                running_on_same_folder=running_on_same_folder,
                python_version=python_version,
            )

    def _import_online_template(
        self, name, running_on_same_folder, template, version, standards, python_version
    ):
        """Create shell based on template downloaded from GitHub by the name."""
        # Create a temp folder for the operation to make sure we delete it after
        with TempDirContext(name) as temp_dir:
            try:
                templates = self.template_retriever.get_templates(standards=standards)
            except (SSLError, FatalError):
                raise click.UsageError(
                    "Cannot retrieve templates list, are you offline?"
                )
            except FeatureUnavailable:
                templates = self.template_retriever.get_templates(
                    alternative=ALTERNATIVE_TEMPLATES_PATH, standards=standards
                )

            templates = {
                template_name: template[0]
                for template_name, template in templates.items()
            }

            if template not in templates:
                raise click.BadParameter(
                    "Template {0} does not exist. "
                    "Supported templates are: {1}".format(
                        template, self._get_templates_with_comma(templates)
                    )
                )
            template_obj = templates[template]

            if not version and template != self.L1_TEMPLATE:
                version = self._get_template_latest_version(
                    standards, template_obj.standard
                )

            try:
                repo_path = self.repository_downloader.download_template(
                    temp_dir, template_obj.repository, version
                )
            except VersionRequestException:
                branches = TemplateVersions(
                    *template_obj.repository.split("/")[-2:]
                ).get_versions_of_template()
                branches.remove(MASTER_BRANCH_NAME)
                branches_str = ", ".join(branches)
                raise click.BadParameter(
                    "Requested standard version ('{}') doesn't match template version."
                    " \nAvailable versions for {}: {}".format(
                        version, template_obj.name, branches_str
                    )
                )

            self._verify_template_standards_compatibility(
                template_path=repo_path, standards=standards
            )

            self.template_compiler.compile_template(
                shell_name=name,
                template_path=repo_path,
                extra_context=template_obj.params,
                running_on_same_folder=running_on_same_folder,
                python_version=python_version,
            )

    def _import_local_template(
        self, name, running_on_same_folder, template, standards, python_version
    ):
        """Create shell based on direct path to local template."""
        repo_path = self._remove_prefix(
            template, NewCommandExecutor.LOCAL_TEMPLATE_URL_PREFIX
        )

        if not os.path.exists(repo_path) or not os.path.isdir(repo_path):
            raise click.BadParameter(
                "Could not locate a template folder at: {template_path}".format(
                    template_path=repo_path
                )
            )

        extra_content = self._get_template_params(repo_path=repo_path)

        self._verify_template_standards_compatibility(
            template_path=repo_path, standards=standards
        )

        self.template_compiler.compile_template(
            shell_name=name,
            template_path=repo_path,
            extra_context=extra_content,
            running_on_same_folder=running_on_same_folder,
            python_version=python_version,
        )

    def _get_template_latest_version(self, standards_list, standard):
        try:
            return self.standard_versions.create(standards_list).get_latest_version(
                standard
            )
        except Exception as e:
            click.ClickException(str(e))

    def _get_local_template_full_path(self, template_name, standards, version=None):
        """Get full path to local template based on provided template name."""
        templates_location = self.cloudshell_config_reader.read().template_location

        templates = self.template_retriever.get_templates(
            template_location=templates_location, standards=standards
        )

        template_obj = templates.get(template_name, None)
        if template_obj is None:
            raise click.BadParameter(
                "There is no template with name ({tmpl_name}).\n"
                "Please, run command 'shellfoundry list' "
                "to get all available templates.".format(tmpl_name=template_name)
            )

        avail_standards = set()
        avail_templates = {}
        for template in template_obj:
            avail_standards.update(standards[template.standard])
            avail_templates.update(template.standard_version)

        if version:
            if version in avail_standards:
                if version in avail_templates:
                    return avail_templates[version]["repo"]
                else:
                    raise click.BadParameter(
                        "Requested template version ({version}) "
                        "does not exist at templates location ({path}).\n"
                        "Existing template versions: {existing_versions}".format(
                            version=version,
                            path=templates_location,
                            existing_versions=", ".join(list(avail_templates.keys())),
                        )
                    )
            else:
                raise click.BadParameter(
                    "Requested template version ({version}) "
                    "does not compatible with available Standards on CloudShell Server"
                    " ({avail_standards})".format(
                        version=version, avail_standards=", ".join(avail_standards)
                    )
                )
        else:
            # try to find max available template version
            try:
                version = str(
                    max(
                        list(
                            map(
                                parse_version,
                                avail_standards & set(avail_templates.keys()),
                            )
                        )
                    )
                )
            except ValueError:
                raise click.ClickException("There are no compatible templates and ")

            return avail_templates[version]["repo"]

    @staticmethod
    def _get_template_params(repo_path):
        """Determine template additional parameters."""
        full_path = os.path.join(repo_path, TEMPLATE_INFO_FILE)
        if not os.path.exists(full_path):
            raise click.ClickException(
                "Wrong template path provided. Provided path: {}".format(repo_path)
            )
        with open(full_path, mode="r", encoding="utf8") as f:
            templ_data = json.load(f)

        family_name = templ_data.get("family_name")
        if isinstance(family_name, list):
            value = click.prompt(
                "Please, choose one of the possible family name: {}".format(
                    ", ".join(family_name)
                ),
                default=family_name[0],
            )
            if value not in family_name:
                raise click.UsageError("Incorrect family name provided.")
            extra_context = {"family_name": value}
        elif family_name:
            extra_context = {"family_name": family_name}
        else:
            extra_context = {}

        return extra_context

    @staticmethod
    def _is_direct_local_template(template):
        return template.startswith(NewCommandExecutor.LOCAL_TEMPLATE_URL_PREFIX)

    @staticmethod
    def _is_direct_online_template(template):
        return template.startswith(NewCommandExecutor.REMOTE_TEMPLATE_URL_PREFIX)

    @staticmethod
    def _remove_prefix(string, prefix):
        return string.rpartition(prefix)[-1]

    @staticmethod
    def _get_templates_with_comma(templates):
        return ", ".join(list(templates.keys()))

    @staticmethod
    def _verify_template_standards_compatibility(template_path, standards):
        """Check is template and available standards on cloudshell are compatible."""
        shell_def_path = os.path.join(
            template_path, "{{cookiecutter.project_slug}}", "shell-definition.yaml"
        )
        if os.path.exists(shell_def_path):
            with open(shell_def_path, encoding="utf8") as stream:
                match = re.search(
                    r"cloudshell_standard:\s*cloudshell_(?P<name>\S+)_standard_(?P<version>\S+)\.\w+$",  # noqa: E501
                    stream.read(),
                    re.MULTILINE,
                )
                if match:
                    name = str(match.groupdict()["name"]).replace("_", "-")
                    version = str(match.groupdict()["version"].replace("_", "."))

                    if name not in standards or version not in standards[name]:
                        raise click.ClickException(
                            "Shell template and available standards are not compatible"
                        )
                else:
                    raise click.ClickException(
                        "Can not determine standard version for provided template"
                    )
