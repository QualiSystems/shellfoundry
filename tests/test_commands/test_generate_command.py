#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys

if sys.version_info >= (3, 0):
    from unittest.mock import MagicMock
else:
    from mock import MagicMock
from pyfakefs import fake_filesystem_unittest

from shellfoundry.commands.generate_command import GenerateCommandExecutor


class TestGenerateCommandExecutor(fake_filesystem_unittest.TestCase):
    def setUp(self):
        self.setUpPyfakefs()

    def test_generate_driver_not_called_on_non_tosca_based_shell(self):
        # Arrange
        self.fs.create_file(
            "nut_shell/shell.yml",
            contents="""
shell:
    name: nut_shell
    driver: NutShellDriver
    """,
        )

        os.chdir("nut_shell")

        driver_generator = MagicMock()

        command_executor = GenerateCommandExecutor(driver_generator=driver_generator)

        # Act
        command_executor.generate()

        # Assert
        driver_generator.generate_driver.assert_not_called()

    def test_generate_driver_called_on_tosca_based_shell(self):
        # Arrange
        self.fs.create_file(
            "nut_shell/shell.yml",
            contents="""
shell:
    name: nut_shell
    driver: NutShellDriver
    """,
        )

        self.fs.create_file(
            "nut_shell/TOSCA-Metadata/TOSCA.meta",
            contents="""
TOSCA-Meta-File-Version: 1.0
CSAR-Version: 0.1.0
Created-By: Anonymous
Entry-Definitions: shell-definition.yml
    """,
        )

        self.fs.create_file(
            "nut_shell/shell-definition.yml",
            contents="""
        metadata:
          template_name: NutShell
        node_types:
          vendor.NutShell:
            artifacts:
              driver:
                file: NutShell.zip
                type: tosca.artifacts.File
                    """,
        )

        os.chdir("nut_shell")

        driver_generator = MagicMock()
        driver_generator.generate_driver = MagicMock()

        command_executor = GenerateCommandExecutor(driver_generator=driver_generator)

        # Act
        command_executor.generate()

        # Assert
        self.assertTrue(driver_generator.generate_driver.called)
        self.assertEqual(
            driver_generator.generate_driver.call_args[1]["shell_filename"],
            "NutShell.zip",
        )
