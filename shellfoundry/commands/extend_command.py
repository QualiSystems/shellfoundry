#!/usr/bin/python
# -*- coding: utf-8 -*-

import click
import os
import shutil
import zipfile


from shellfoundry.utilities.config_reader import Configuration, CloudShellConfigReader
from shellfoundry.utilities.constants import TEMPLATE_AUTHOR_FIELD, METADATA_AUTHOR_FIELD, TEMPLATE_BASED_ON
from shellfoundry.utilities.modifiers.definition.definition_modification import DefinitionModification
from shellfoundry.utilities.repository_downloader import RepositoryDownloader
from shellfoundry.utilities.temp_dir_context import TempDirContext
from shellfoundry.utilities.validations import ShellNameValidations, ShellGenerationValidations
from shellfoundry.exceptions import VersionRequestException


class ExtendCommandExecutor(object):
    LOCAL_TEMPLATE_URL_PREFIX = "local:"
    SIGN_FILENAME = "signed"

    def __init__(self, repository_downloader=None, shell_name_validations=None, shell_gen_validations=None):
        """
        :param RepositoryDownloader repository_downloader:
        :param ShellNameValidations shell_name_validations:
        """
        self.repository_downloader = repository_downloader or RepositoryDownloader()
        self.shell_name_validations = shell_name_validations or ShellNameValidations()
        self.shell_gen_validations = shell_gen_validations or ShellGenerationValidations()
        self.cloudshell_config_reader = Configuration(CloudShellConfigReader())

    def extend(self, name, source, attribute_names):
        """ Create a new shell based on a already existed shell
        :param str name: The name of the Shell
        :param str source: The path to existed Shell. Can be url or local path
        :param tuple attribute_names: Sequence of attribute names that should be added
        """

        if name == os.path.curdir:
            name = os.path.split(os.getcwd())[1]
            shell_dir = os.path.join(os.path.pardir, name)
        else:
            shell_dir = os.path.join(os.path.curdir, name)

        if os.path.exists(shell_dir):
            raise click.BadParameter(u"Extended Shell folder '{}' already exist.".format(os.path.abspath(shell_dir)))

        if not self.shell_name_validations.validate_shell_name(name):
            raise click.BadParameter(
                u"Shell name must begin with a letter and contain only alpha-numeric characters and spaces.")

        with TempDirContext(name) as temp_dir:
            try:
                if self._is_local(source):
                    shell_path = self._copy_local_shell(name,
                                                        self._remove_prefix(source,
                                                                            ExtendCommandExecutor.LOCAL_TEMPLATE_URL_PREFIX),
                                                        temp_dir)
                else:
                    shell_path = self._copy_online_shell(source, temp_dir)
            except VersionRequestException as err:
                raise click.ClickException(err.message)
            except Exception:
                raise click.BadParameter(u"Check correctness of entered attributes")

            if not self.shell_gen_validations.validate_2nd_gen(shell_path):
                raise click.ClickException(u"Invalid second generation Shell.")

            self._remove_quali_signature(shell_path)

            modificator = DefinitionModification(shell_path)
            self._change_author(shell_path, modificator)
            self._add_based_on(shell_path, modificator)
            self._add_attributes(shell_path, attribute_names)

            shutil.move(shell_path, shell_dir)

        click.echo("Created shell {0} based on source {1}".format(name, source))

    def _copy_local_shell(self, name, source, destination):
        """ Copy shell and extract if needed """

        if os.path.isdir(source):
            ext_shell_path = os.path.join(destination, name)
            shutil.copytree(source, ext_shell_path)
        elif zipfile.is_zipfile(source):
            ext_shell_path = self.repository_downloader.repo_extractor.extract_to_folder(source, destination)[0]
            if not os.path.isdir(ext_shell_path):
                ext_shell_path = os.path.dirname(ext_shell_path)
            ext_shell_path = os.path.join(destination, ext_shell_path)
        else:
            raise

        return ext_shell_path

    def _copy_online_shell(self, source, destination):
        """ Download shell and extract it """

        archive_path = None
        try:
            archive_path = self.repository_downloader.download_file(source, destination)
            ext_shell_path = self.repository_downloader.repo_extractor.extract_to_folder(archive_path, destination)
            ext_shell_path = ext_shell_path[0]
        finally:
            if archive_path and os.path.exists(archive_path):
                os.remove(archive_path)

        return os.path.join(destination, ext_shell_path)

    @staticmethod
    def _is_local(source):
        return source.startswith(ExtendCommandExecutor.LOCAL_TEMPLATE_URL_PREFIX)

    @staticmethod
    def _remove_prefix(string, prefix):
        return string.rpartition(prefix)[-1]

    @staticmethod
    def _remove_quali_signature(shell_path):
        """ Remove Quali signature from shell """

        signature_file_path = os.path.join(shell_path, ExtendCommandExecutor.SIGN_FILENAME)
        if os.path.exists(signature_file_path):
            os.remove(signature_file_path)

    def _change_author(self, shell_path, modificator=None):
        """ Change shell authoring """

        author = self.cloudshell_config_reader.read().author

        if not modificator:
            modificator = DefinitionModification(shell_path)

        modificator.edit_definition(field=TEMPLATE_AUTHOR_FIELD, value=author)
        modificator.edit_tosca_meta(field=METADATA_AUTHOR_FIELD, value=author)

    def _add_based_on(self, shell_path, modificator=None):
        """ Add Based_ON field to shell-definition.yaml file """

        if not modificator:
            modificator = DefinitionModification(shell_path)

        modificator.add_field_to_definition(field=TEMPLATE_BASED_ON)

    def _add_attributes(self, shell_path, attribute_names, modificator=None):
        """ Add a commented out attributes to the shell definition """

        if not modificator:
            modificator = DefinitionModification(shell_path)

        modificator.add_properties(attribute_names=attribute_names)
