#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import re
import shutil

import click

from shellfoundry.exceptions import VersionRequestException
from shellfoundry.utilities.config_reader import CloudShellConfigReader, Configuration
from shellfoundry.utilities.constants import (
    METADATA_AUTHOR_FIELD,
    TEMPLATE_AUTHOR_FIELD,
    TEMPLATE_BASED_ON,
)
from shellfoundry.utilities.modifiers.definition.definition_modification import (
    DefinitionModification,
)
from shellfoundry.utilities.repository_downloader import RepositoryDownloader
from shellfoundry.utilities.temp_dir_context import TempDirContext
from shellfoundry.utilities.validations import (
    ShellGenerationValidations,
    ShellNameValidations,
)


class ExtendCommandExecutor(object):
    LOCAL_TEMPLATE_URL_PREFIX = "local:"
    SIGN_FILENAME = "signed"
    ARTIFACTS = {"driver": "src", "deployment": "deployments"}

    def __init__(
        self,
        repository_downloader=None,
        shell_name_validations=None,
        shell_gen_validations=None,
    ):
        """Creates a new shell based on an already existing shell.

        :param RepositoryDownloader repository_downloader:
        :param ShellNameValidations shell_name_validations:
        """
        self.repository_downloader = repository_downloader or RepositoryDownloader()
        self.shell_name_validations = shell_name_validations or ShellNameValidations()
        self.shell_gen_validations = (
            shell_gen_validations or ShellGenerationValidations()
        )
        self.cloudshell_config_reader = Configuration(CloudShellConfigReader())

    def extend(self, source, attribute_names):
        """Create a new shell based on an already existing shell.

        :param str source: The path to the existing shell. Can be a url or local path
        :param tuple attribute_names: Sequence of attribute names that should be added
        """
        with TempDirContext("Extended_Shell_Temp_Dir") as temp_dir:
            try:
                if self._is_local(source):
                    temp_shell_path = self._copy_local_shell(
                        self._remove_prefix(
                            source, ExtendCommandExecutor.LOCAL_TEMPLATE_URL_PREFIX
                        ),
                        temp_dir,
                    )
                else:
                    temp_shell_path = self._copy_online_shell(source, temp_dir)
            except VersionRequestException as err:
                raise click.ClickException(str(err))
            except Exception:
                raise click.BadParameter("Check correctness of entered attributes")

            # Remove shell version from folder name
            shell_path = re.sub(r"-\d+(\.\d+)*/?$", "", temp_shell_path)
            os.rename(temp_shell_path, shell_path)

            if not self.shell_gen_validations.validate_2nd_gen(shell_path):
                raise click.ClickException("Invalid second generation Shell.")

            modificator = DefinitionModification(shell_path)
            self._unpack_driver_archive(shell_path, modificator)
            self._remove_quali_signature(shell_path)
            self._change_author(shell_path, modificator)
            self._add_based_on(shell_path, modificator)
            self._add_attributes(shell_path, attribute_names)

            try:
                shutil.move(shell_path, os.path.curdir)
            except shutil.Error as err:
                raise click.BadParameter(str(err))

        click.echo("Created shell based on source {}".format(source))

    def _copy_local_shell(self, source, destination):
        """Copy shell and extract if needed."""
        if os.path.isdir(source):
            source = source.rstrip(os.sep)
            name = os.path.basename(source)
            ext_shell_path = os.path.join(destination, name)
            shutil.copytree(source, ext_shell_path)
        else:
            raise

        return ext_shell_path

    def _copy_online_shell(self, source, destination):
        """Download shell and extract it."""
        archive_path = None
        try:
            archive_path = self.repository_downloader.download_file(source, destination)
            ext_shell_path = (
                self.repository_downloader.repo_extractor.extract_to_folder(
                    archive_path, destination
                )
            )
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

    def _unpack_driver_archive(self, shell_path, modificator=None):
        """Unpack driver files from ZIP-archive."""
        if not modificator:
            modificator = DefinitionModification(shell_path)

        artifacts = modificator.get_artifacts_files(
            artifact_name_list=list(self.ARTIFACTS.keys())
        )

        for artifact_name, artifact_path in artifacts.items():

            artifact_path = os.path.join(shell_path, artifact_path)

            if os.path.exists(artifact_path):
                self.repository_downloader.repo_extractor.extract_to_folder(
                    artifact_path,
                    os.path.join(shell_path, self.ARTIFACTS[artifact_name]),
                )
                os.remove(artifact_path)

    @staticmethod
    def _remove_quali_signature(shell_path):
        """Remove Quali signature from shell."""
        signature_file_path = os.path.join(
            shell_path, ExtendCommandExecutor.SIGN_FILENAME
        )
        if os.path.exists(signature_file_path):
            os.remove(signature_file_path)

    def _change_author(self, shell_path, modificator=None):
        """Change shell authoring."""
        author = self.cloudshell_config_reader.read().author

        if not modificator:
            modificator = DefinitionModification(shell_path)

        modificator.edit_definition(field=TEMPLATE_AUTHOR_FIELD, value=author)
        modificator.edit_tosca_meta(field=METADATA_AUTHOR_FIELD, value=author)

    def _add_based_on(self, shell_path, modificator=None):
        """Add Based_ON field to shell-definition.yaml file."""
        if not modificator:
            modificator = DefinitionModification(shell_path)

        modificator.add_field_to_definition(field=TEMPLATE_BASED_ON)

    def _add_attributes(self, shell_path, attribute_names, modificator=None):
        """Add a commented out attributes to the shell definition."""
        if not modificator:
            modificator = DefinitionModification(shell_path)

        modificator.add_properties(attribute_names=attribute_names)
