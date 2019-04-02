#!/usr/bin/python
# -*- coding: utf-8 -*-

import unittest

from pyfakefs import fake_filesystem_unittest
from shellfoundry.utilities.shell_package import ShellPackage


class TestShellPackage(unittest.TestCase):
    def test_get_shell_name_should_be_capitalized(self):
        # Arrange
        shell_package = ShellPackage('work/folders/nut-shell')

        # Act
        shell_name = shell_package.get_shell_name()

        # Assert
        self.assertEqual(shell_name, 'NutShell')

    def test_get_shell_name_with_underscore_should_be_capitalized_and_be_without_underscore(self):
        # Arrange
        shell_package = ShellPackage('work/folders/nut_shell')

        # Act
        shell_name = shell_package.get_shell_name()

        # Assert
        self.assertEqual(shell_name, 'NutShell')

    def test_is_layer_one(self):
        # Arrange
        shell_package = ShellPackage('work/folders/cloudshell-L1-test')

        # Assert
        self.assertTrue(shell_package.is_layer_one())


class TestShellPackageWithFileSystem(fake_filesystem_unittest.TestCase):
    def setUp(self):
        self.setUpPyfakefs()

    def test_get_shell_from_definition(self):
        # Arrange
        self.fs.CreateFile('work/nut-shell/TOSCA-Metadata/TOSCA.meta',
                           contents='TOSCA-Meta-File-Version: 1.0\n'
                                    'CSAR-Version: 0.1.0\n'
                                    'Created-By: Anonymous\n'
                                    'Entry-Definitions: shell-definition.yaml')
        self.fs.CreateFile('work/nut-shell/shell-definition.yaml',
                           contents='tosca_definitions_version: tosca_simple_yaml_1_0\n'
                                    'metadata:\n'
                                    '  template_name: NutShell\n'
                                    '  template_author: Anonymous\n'
                                    '  template_version: 1.0.0\n'
                                    'node_types:\n'
                                    '  vendor.switch.NXOS:\n'
                                    '    derived_from: cloudshell.nodes.Switch\n'
                                    '    artifacts:\n'
                                    '      icon:\n'
                                    '        file: nxos.png\n'
                                    '        type: tosca.artifacts.File\n'
                                    '      driver:\n'
                                    '        file: NutShellDriver.zip\n'
                                    '        type: tosca.artifacts.File')

        shell_package = ShellPackage('work/nut-shell')

        # Act
        shell_name = shell_package.get_name_from_definition()

        # Assert
        self.assertEqual(shell_name, 'NutShell')

    def test_get_shell_from_definition_with_hard_reload(self):
        # Arrange
        self.fs.CreateFile('work/nut-shell/TOSCA-Metadata/TOSCA.meta',
                           contents='TOSCA-Meta-File-Version: 1.0\n'
                                    'CSAR-Version: 0.1.0\n'
                                    'Created-By: Anonymous\n'
                                    'Entry-Definitions: shell-definition.yaml')
        self.fs.CreateFile('work/nut-shell/shell-definition.yaml',
                           contents='tosca_definitions_version: tosca_simple_yaml_1_0\n'
                                    'metadata:\n'
                                    '  template_name: NutShell\n'
                                    '  template_author: Anonymous\n'
                                    '  template_version: 1.0.0\n'
                                    'node_types:\n'
                                    '  vendor.switch.NXOS:\n'
                                    '    derived_from: cloudshell.nodes.Switch\n'
                                    '    artifacts:\n'
                                    '      icon:\n'
                                    '        file: nxos.png\n'
                                    '        type: tosca.artifacts.File\n'
                                    '      driver:\n'
                                    '        file: NutShellDriver.zip\n'
                                    '        type: tosca.artifacts.File')

        shell_package = ShellPackage('work/nut-shell')
        shell_package.real_shell_name = "something"

        # Act
        shell_name = shell_package.get_name_from_definition(should_reload=True)

        # Assert
        self.assertEqual(shell_name, 'NutShell')
