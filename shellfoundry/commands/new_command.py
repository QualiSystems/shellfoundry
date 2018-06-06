#!/usr/bin/python
# -*- coding: utf-8 -*-

import click
import os
import json

from requests.exceptions import SSLError

from cloudshell.rest.exceptions import FeatureUnavailable
from ..exceptions import FatalError

from shellfoundry import ALTERNATIVE_STANDARDS_PATH, ALTERNATIVE_TEMPLATES_PATH, MASTER_BRANCH_NAME
from shellfoundry.exceptions import VersionRequestException
from shellfoundry.utilities.constants import TEMPLATE_INFO_FILE
from shellfoundry.utilities.cookiecutter_integration import CookiecutterTemplateCompiler
from shellfoundry.utilities.repository_downloader import RepositoryDownloader
from shellfoundry.utilities.standards import StandardVersionsFactory, Standards
from shellfoundry.utilities.temp_dir_context import TempDirContext
from shellfoundry.utilities.template_retriever import TemplateRetriever
from shellfoundry.utilities.template_versions import TemplateVersions
from shellfoundry.utilities.validations import ShellNameValidations


class NewCommandExecutor(object):
    LOCAL_TEMPLATE_URL_PREFIX = 'local:'

    def __init__(self, template_compiler=None,
                 template_retriever=None,
                 repository_downloader=None,
                 standards=None,
                 standard_versions=None,
                 shell_name_validations=None):
        """
        :param CookiecutterTemplateCompiler template_compiler:
        :param TemplateRetriever template_retriever:
        :param RepositoryDownloader repository_downloader:
        :param Standards standards:
        :param StandardVersionsFactory standard_versions:
        :param ShellNameValidations shell_name_validations:
        """
        self.template_retriever = template_retriever or TemplateRetriever()
        self.repository_downloader = repository_downloader or RepositoryDownloader()
        self.template_compiler = template_compiler or CookiecutterTemplateCompiler()
        self.standards = standards or Standards()
        self.standard_versions = standard_versions or StandardVersionsFactory()
        self.shell_name_validations = shell_name_validations or ShellNameValidations()

    def new(self, name, template, version=None):
        """
        Create a new shell based on a template.
        :param str version: The desired version of the shell template to use
        :param str name: The name of the Shell
        :param str template: The name of the template to use
        """
        # Special handling for the case where the user runs 'shellfoundry .' in such a case the '.'
        # character is substituted for the shell name and the content of the current folder is populated
        running_on_same_folder = False
        if name == os.path.curdir:
            name = os.path.split(os.getcwd())[1]
            running_on_same_folder = True

        if not self.shell_name_validations.validate_shell_name(name):
            raise click.BadParameter(
                u"Shell name must begin with a letter and contain only alpha-numeric characters and spaces.")

        if self._is_local_template(template):
            self._import_local_template(name, running_on_same_folder, template)

        else:
            self._import_online_template(name, running_on_same_folder, template, version)

        click.echo('Created shell {0} based on template {1}'.format(name, template))

    def _import_online_template(self, name, running_on_same_folder, template, version):
        # Create a temp folder for the operation to make sure we delete it after
        with TempDirContext(name) as temp_dir:
            try:
                standards = self.standards.fetch()
                templates = self.template_retriever.get_templates(standards=standards)
            except (SSLError, FatalError):
                raise click.UsageError("Cannot retrieve templates list, are you offline?")
            except FeatureUnavailable:
                standards = self.standards.fetch(alternative=ALTERNATIVE_STANDARDS_PATH)
                templates = self.template_retriever.get_templates(
                    alternative=ALTERNATIVE_TEMPLATES_PATH, standards=standards)

            if template not in templates:
                raise click.BadParameter(
                    u'Template {0} does not exist. Supported templates are: {1}'.format(template,
                                                                                        self._get_templates_with_comma(
                                                                                            templates)))
            template_obj = templates[template]

            if not version:
                version = self._get_template_latest_version(standards, template_obj.standard)

            try:
                repo_path = self.repository_downloader.download_template(temp_dir, template_obj.repository, version)
            except VersionRequestException:
                branches = TemplateVersions(*template_obj.repository.split('/')[-2:]).get_versions_of_template()
                branches.remove(MASTER_BRANCH_NAME)
                branches_str = ', '.join(branches)
                raise click.BadParameter(
                    u'Requested standard version (\'{}\') does not match '
                    u'template version. \nAvailable versions for {}: {}'
                    .format(version, template_obj.name, branches_str))

            self.template_compiler.compile_template(shell_name=name,
                                                    template_path=repo_path,
                                                    extra_context=template_obj.params,
                                                    running_on_same_folder=running_on_same_folder)

    def _get_template_latest_version(self, standards_list, standard):
        try:
            return self.standard_versions.create(standards_list).get_latest_version(standard)
        except Exception as e:
            click.ClickException(e.message)

    def _import_local_template(self, name, running_on_same_folder, template):
        repo_path = self._remove_prefix(template, NewCommandExecutor.LOCAL_TEMPLATE_URL_PREFIX)

        if not os.path.exists(repo_path) or not os.path.isdir(repo_path):
            raise click.BadParameter("Could not locate a template folder at: {template_path}"
                                     .format(template_path=repo_path))

        full_path = os.path.join(repo_path, TEMPLATE_INFO_FILE)
        with open(full_path, mode='r') as f:
            templ_data = json.load(f)

        family_name = templ_data.get("family_name")
        if isinstance(family_name, list):
            value = click.prompt("Please, choose one of the possible family name: {}".format(", ".join(family_name)),
                                 default=family_name[0])
            if value not in family_name:
                raise click.UsageError("Incorrect family name provided.")
            extra_context = {"family_name": value}
        elif family_name:
            extra_context = {"family_name": family_name}
        else:
            extra_context = {}

        self.template_compiler.compile_template(shell_name=name,
                                                template_path=repo_path,
                                                extra_context=extra_context,
                                                running_on_same_folder=running_on_same_folder)

    def _is_local_template(self, template):
        return template.startswith(NewCommandExecutor.LOCAL_TEMPLATE_URL_PREFIX)

    def _remove_prefix(self, string, prefix):
        return string.rpartition(prefix)[-1]

    @staticmethod
    def _get_templates_with_comma(templates):
        return ', '.join(templates.keys())
