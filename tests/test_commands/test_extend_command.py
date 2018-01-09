#!/usr/bin/python
# -*- coding: utf-8 -*-

import mock
import unittest
import shutil
import os

from click import BadParameter, ClickException


from shellfoundry.exceptions import VersionRequestException
from shellfoundry.utilities.constants import TEMPLATE_AUTHOR_FIELD, METADATA_AUTHOR_FIELD, TEMPLATE_BASED_ON

from click import UsageError
from requests.exceptions import SSLError
from cloudshell.rest.api import FeatureUnavailable
from shellfoundry import ALTERNATIVE_TEMPLATES_PATH, ALTERNATIVE_STANDARDS_PATH
from shellfoundry.commands.new_command import NewCommandExecutor
from shellfoundry.models.shell_template import ShellTemplate
from shellfoundry.utilities.cookiecutter_integration import CookiecutterTemplateCompiler
from shellfoundry.utilities.template_retriever import TemplateRetriever
from shellfoundry.utilities.repository_downloader import RepositoryDownloader
from shellfoundry.utilities.temp_dir_context import TempDirContext
from shellfoundry.utilities.standards import StandardVersionsFactory, Standards
from shellfoundry.utilities.template_versions import TemplateVersions
from shellfoundry.utilities.template_retriever import TEMPLATES_YML


from shellfoundry.commands.extend_command import ExtendCommandExecutor


class TestExtendCommandExecutor(unittest.TestCase):

    def setUp(self):
        super(TestExtendCommandExecutor, self).setUp()
        repository_downloader = mock.MagicMock
        shell_name_validations = mock.MagicMock
        with mock.patch("shellfoundry.commands.extend_command.Configuration"):
            self.tested_instance = ExtendCommandExecutor(repository_downloader=repository_downloader,
                                                         shell_name_validations=shell_name_validations,
                                                         shell_gen_validations=None)

    def tearDown(self):
        super(TestExtendCommandExecutor, self).tearDown()
        del self.tested_instance

    @mock.patch("shellfoundry.commands.extend_command.ExtendCommandExecutor._copy_local_shell",
                new=mock.MagicMock(side_effect=Exception))
    def test_extend_incorrect_arguments(self):

        with mock.patch("shellfoundry.commands.extend_command.TempDirContext"):
            with self.assertRaisesRegexp(BadParameter, u"Check correctness of entered attributes"):
                self.tested_instance.extend("local:some_path", ("new_attribute",))

    @mock.patch("shellfoundry.commands.extend_command.ShellGenerationValidations.validate_2nd_gen",
                new=mock.MagicMock(return_value=True))
    @mock.patch("shellfoundry.commands.extend_command.ExtendCommandExecutor._copy_local_shell",
                new=mock.MagicMock(return_value="extended_shell_path"))
    @mock.patch("shellfoundry.commands.extend_command.ExtendCommandExecutor._unpack_driver_archive",
                new=mock.MagicMock())
    @mock.patch("shellfoundry.commands.extend_command.os", new=mock.MagicMock())
    @mock.patch("shellfoundry.commands.extend_command.shutil", new=mock.MagicMock())
    def test_extend_from_local_success(self):

        with mock.patch("shellfoundry.commands.extend_command.TempDirContext"):
            with mock.patch("shellfoundry.commands.extend_command.DefinitionModification"):
                self.tested_instance.extend("local:some_path", ("new_attribute",))

    @mock.patch("shellfoundry.commands.extend_command.ShellGenerationValidations.validate_2nd_gen",
                new=mock.MagicMock(return_value=True))
    @mock.patch("shellfoundry.commands.extend_command.ExtendCommandExecutor._copy_online_shell",
                new=mock.MagicMock(return_value="extended_shell_path"))
    @mock.patch("shellfoundry.commands.extend_command.ExtendCommandExecutor._unpack_driver_archive",
                new=mock.MagicMock())
    @mock.patch("shellfoundry.commands.extend_command.os", new=mock.MagicMock())
    @mock.patch("shellfoundry.commands.extend_command.shutil", new=mock.MagicMock())
    def test_extend_from_remote_success(self):
        with mock.patch("shellfoundry.commands.extend_command.TempDirContext"):
            with mock.patch("shellfoundry.commands.extend_command.DefinitionModification"):
                self.tested_instance.extend("some_path", ("new_attribute",))

    @mock.patch("shellfoundry.commands.extend_command.ExtendCommandExecutor._copy_online_shell",
                new=mock.MagicMock(side_effect=VersionRequestException))
    def test_extend_from_remote_download_failed(self):
        with mock.patch("shellfoundry.commands.extend_command.TempDirContext"):
            with self.assertRaises(ClickException):
                self.tested_instance.extend("some_path", ("new_attribute",))

    @mock.patch("shellfoundry.commands.extend_command.os.rename", new=mock.MagicMock())
    @mock.patch("shellfoundry.commands.extend_command.ShellGenerationValidations.validate_2nd_gen",
                new=mock.MagicMock(return_value=False))
    @mock.patch("shellfoundry.commands.extend_command.ExtendCommandExecutor._copy_online_shell",
                new=mock.MagicMock(return_value="extended_shell_path"))
    def test_extend_not_2_gen_shell(self):
        with mock.patch("shellfoundry.commands.extend_command.TempDirContext"):
            with self.assertRaisesRegexp(ClickException, u"Invalid second generation Shell."):
                self.tested_instance.extend("some_path", ("new_attribute",))

    @mock.patch("shellfoundry.commands.extend_command.ShellGenerationValidations.validate_2nd_gen",
                new=mock.MagicMock(return_value=True))
    @mock.patch("shellfoundry.commands.extend_command.ExtendCommandExecutor._copy_local_shell",
                new=mock.MagicMock(return_value="extended_shell_path"))
    @mock.patch("shellfoundry.commands.extend_command.ExtendCommandExecutor._unpack_driver_archive",
                new=mock.MagicMock())
    @mock.patch("shellfoundry.commands.extend_command.os", new=mock.MagicMock())
    @mock.patch("shellfoundry.commands.extend_command.shutil.move", new=mock.MagicMock(side_effect=shutil.Error))
    def test_extend_failed_copy_from_temp_folder(self):
        with mock.patch("shellfoundry.commands.extend_command.TempDirContext"):
            with mock.patch("shellfoundry.commands.extend_command.DefinitionModification"):
                with self.assertRaises(BadParameter):
                    self.tested_instance.extend("local:some_path", ("new_attribute",))

    @mock.patch("shellfoundry.commands.extend_command.os.path.isdir", new=mock.MagicMock(return_value=True))
    @mock.patch("shellfoundry.commands.extend_command.shutil", new=mock.MagicMock())
    def test___copy_local_shell_success(self):
        self.tested_instance._copy_local_shell("source_shell_path", "destination_shell_path")

    @mock.patch("shellfoundry.commands.extend_command.os.path.isdir", new=mock.MagicMock(return_value=False))
    @mock.patch("shellfoundry.commands.extend_command.shutil", new=mock.MagicMock())
    def test___copy_local_shell_failed_source_not_a_folder(self):
        with self.assertRaises(Exception):
            self.tested_instance._copy_local_shell("source_shell_path", "destination_shell_path")

    @mock.patch("shellfoundry.commands.extend_command.os.path.isdir", new=mock.MagicMock(return_value=True))
    @mock.patch("shellfoundry.commands.extend_command.shutil.copytree", new=mock.MagicMock(side_effect=Exception))
    def test___copy_local_shell_failed_copy_shell(self):
        with self.assertRaises(Exception):
            self.tested_instance._copy_local_shell("source_shell_path", "destination_shell_path")

    @mock.patch("shellfoundry.commands.extend_command.DefinitionModification")
    def test__add_based_on_success(self, definition_modification_class):
        modificator = mock.MagicMock()
        definition_modification_class.return_value = modificator

        self.tested_instance._add_based_on("shell_path", modificator)

        modificator.add_field_to_definition.assert_called_once_with(field=TEMPLATE_BASED_ON)

    @mock.patch("shellfoundry.commands.extend_command.DefinitionModification")
    def test__add_based_on_without_modificator(self, definition_modification_class):
        modificator = mock.MagicMock()
        definition_modification_class.return_value = modificator

        self.tested_instance._add_based_on("shell_path")

        modificator.add_field_to_definition.assert_called_once_with(field=TEMPLATE_BASED_ON)

    @mock.patch("shellfoundry.commands.extend_command.DefinitionModification")
    def test__add_attributes_success(self, definition_modification_class):

        attr_names = ["attr_1", "attr_2"]
        modificator = mock.MagicMock()
        definition_modification_class.return_value = modificator

        self.tested_instance._add_attributes("shell_path", attr_names, modificator)

        modificator.add_properties.assert_called_once_with(attribute_names=attr_names)

    @mock.patch("shellfoundry.commands.extend_command.DefinitionModification")
    def test__add_attributes_without_modificator(self, definition_modification_class):

        attr_names = ["attr_1", "attr_2"]
        modificator = mock.MagicMock()
        definition_modification_class.return_value = modificator

        self.tested_instance._add_attributes("shell_path", attr_names)

        modificator.add_properties.assert_called_once_with(attribute_names=attr_names)
