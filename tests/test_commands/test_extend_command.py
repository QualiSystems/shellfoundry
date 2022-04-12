#!/usr/bin/python
# -*- coding: utf-8 -*-

import shutil
import sys
import unittest

if sys.version_info >= (3, 0):
    from unittest.mock import MagicMock, patch
else:
    from mock import MagicMock, patch

from click import BadParameter, ClickException

from shellfoundry.commands.extend_command import ExtendCommandExecutor
from shellfoundry.exceptions import VersionRequestException
from shellfoundry.utilities.constants import TEMPLATE_BASED_ON


class TestExtendCommandExecutor(unittest.TestCase):
    def setUp(self):
        super(TestExtendCommandExecutor, self).setUp()
        repository_downloader = MagicMock
        shell_name_validations = MagicMock
        with patch("shellfoundry.commands.extend_command.Configuration"):
            self.tested_instance = ExtendCommandExecutor(
                repository_downloader=repository_downloader,
                shell_name_validations=shell_name_validations,
                shell_gen_validations=None,
            )

    def tearDown(self):
        super(TestExtendCommandExecutor, self).tearDown()
        del self.tested_instance

    @patch(
        "shellfoundry.commands.extend_command.ExtendCommandExecutor._copy_local_shell",
        new=MagicMock(side_effect=Exception),
    )
    def test_extend_incorrect_arguments(self):

        with patch("shellfoundry.commands.extend_command.TempDirContext"):
            with self.assertRaisesRegex(
                BadParameter, "Check correctness of entered attributes"
            ):
                self.tested_instance.extend("local:some_path", ("new_attribute",))

    @patch(
        "shellfoundry.commands.extend_command.ShellGenerationValidations.validate_2nd_gen",  # noqa: E501
        new=MagicMock(return_value=True),
    )
    @patch(
        "shellfoundry.commands.extend_command.ExtendCommandExecutor._copy_local_shell",
        new=MagicMock(return_value="extended_shell_path"),
    )
    @patch(
        "shellfoundry.commands.extend_command.ExtendCommandExecutor._unpack_driver_archive",  # noqa: E501
        new=MagicMock(),
    )
    @patch("shellfoundry.commands.extend_command.os", new=MagicMock())
    @patch("shellfoundry.commands.extend_command.shutil", new=MagicMock())
    def test_extend_from_local_success(self):

        with patch("shellfoundry.commands.extend_command.TempDirContext"):
            with patch("shellfoundry.commands.extend_command.DefinitionModification"):
                self.tested_instance.extend("local:some_path", ("new_attribute",))

    @patch(
        "shellfoundry.commands.extend_command.ShellGenerationValidations.validate_2nd_gen",  # noqa: E501
        new=MagicMock(return_value=True),
    )
    @patch(
        "shellfoundry.commands.extend_command.ExtendCommandExecutor._copy_online_shell",
        new=MagicMock(return_value="extended_shell_path"),
    )
    @patch(
        "shellfoundry.commands.extend_command.ExtendCommandExecutor._unpack_driver_archive",  # noqa: E501
        new=MagicMock(),
    )
    @patch("shellfoundry.commands.extend_command.os", new=MagicMock())
    @patch("shellfoundry.commands.extend_command.shutil", new=MagicMock())
    def test_extend_from_remote_success(self):
        with patch("shellfoundry.commands.extend_command.TempDirContext"):
            with patch("shellfoundry.commands.extend_command.DefinitionModification"):
                self.tested_instance.extend("some_path", ("new_attribute",))

    @patch(
        "shellfoundry.commands.extend_command.ExtendCommandExecutor._copy_online_shell",
        new=MagicMock(side_effect=VersionRequestException),
    )
    def test_extend_from_remote_download_failed(self):
        with patch("shellfoundry.commands.extend_command.TempDirContext"):
            with self.assertRaises(ClickException):
                self.tested_instance.extend("some_path", ("new_attribute",))

    @patch("shellfoundry.commands.extend_command.os.rename", new=MagicMock())
    @patch(
        "shellfoundry.commands.extend_command.ShellGenerationValidations.validate_2nd_gen",  # noqa: E501
        new=MagicMock(return_value=False),
    )
    @patch(
        "shellfoundry.commands.extend_command.ExtendCommandExecutor._copy_online_shell",
        new=MagicMock(return_value="extended_shell_path"),
    )
    def test_extend_not_2_gen_shell(self):
        with patch("shellfoundry.commands.extend_command.TempDirContext"):
            with self.assertRaisesRegex(
                ClickException, "Invalid second generation Shell."
            ):
                self.tested_instance.extend("some_path", ("new_attribute",))

    @patch(
        "shellfoundry.commands.extend_command.ShellGenerationValidations.validate_2nd_gen",  # noqa: E501
        new=MagicMock(return_value=True),
    )
    @patch(
        "shellfoundry.commands.extend_command.ExtendCommandExecutor._copy_local_shell",
        new=MagicMock(return_value="extended_shell_path"),
    )
    @patch(
        "shellfoundry.commands.extend_command.ExtendCommandExecutor._unpack_driver_archive",  # noqa: E501
        new=MagicMock(),
    )
    @patch("shellfoundry.commands.extend_command.os", new=MagicMock())
    @patch(
        "shellfoundry.commands.extend_command.shutil.move",
        new=MagicMock(side_effect=shutil.Error),
    )
    def test_extend_failed_copy_from_temp_folder(self):
        with patch("shellfoundry.commands.extend_command.TempDirContext"):
            with patch("shellfoundry.commands.extend_command.DefinitionModification"):
                with self.assertRaises(BadParameter):
                    self.tested_instance.extend("local:some_path", ("new_attribute",))

    @patch(
        "shellfoundry.commands.extend_command.os.path.isdir",
        new=MagicMock(return_value=True),
    )
    @patch("shellfoundry.commands.extend_command.shutil", new=MagicMock())
    def test___copy_local_shell_success(self):
        self.tested_instance._copy_local_shell(
            "source_shell_path", "destination_shell_path"
        )

    @patch(
        "shellfoundry.commands.extend_command.os.path.isdir",
        new=MagicMock(return_value=False),
    )
    @patch("shellfoundry.commands.extend_command.shutil", new=MagicMock())
    def test___copy_local_shell_failed_source_not_a_folder(self):
        with self.assertRaises(Exception):
            self.tested_instance._copy_local_shell(
                "source_shell_path", "destination_shell_path"
            )

    @patch(
        "shellfoundry.commands.extend_command.os.path.isdir",
        new=MagicMock(return_value=True),
    )
    @patch(
        "shellfoundry.commands.extend_command.shutil.copytree",
        new=MagicMock(side_effect=Exception),
    )
    def test___copy_local_shell_failed_copy_shell(self):
        with self.assertRaises(Exception):
            self.tested_instance._copy_local_shell(
                "source_shell_path", "destination_shell_path"
            )

    @patch("shellfoundry.commands.extend_command.DefinitionModification")
    def test__add_based_on_success(self, definition_modification_class):
        modificator = MagicMock()
        definition_modification_class.return_value = modificator

        self.tested_instance._add_based_on("shell_path", modificator)

        modificator.add_field_to_definition.assert_called_once_with(
            field=TEMPLATE_BASED_ON
        )

    @patch("shellfoundry.commands.extend_command.DefinitionModification")
    def test__add_based_on_without_modificator(self, definition_modification_class):
        modificator = MagicMock()
        definition_modification_class.return_value = modificator

        self.tested_instance._add_based_on("shell_path")

        modificator.add_field_to_definition.assert_called_once_with(
            field=TEMPLATE_BASED_ON
        )

    @patch("shellfoundry.commands.extend_command.DefinitionModification")
    def test__add_attributes_success(self, definition_modification_class):

        attr_names = ["attr_1", "attr_2"]
        modificator = MagicMock()
        definition_modification_class.return_value = modificator

        self.tested_instance._add_attributes("shell_path", attr_names, modificator)

        modificator.add_properties.assert_called_once_with(attribute_names=attr_names)

    @patch("shellfoundry.commands.extend_command.DefinitionModification")
    def test__add_attributes_without_modificator(self, definition_modification_class):

        attr_names = ["attr_1", "attr_2"]
        modificator = MagicMock()
        definition_modification_class.return_value = modificator

        self.tested_instance._add_attributes("shell_path", attr_names)

        modificator.add_properties.assert_called_once_with(attribute_names=attr_names)
