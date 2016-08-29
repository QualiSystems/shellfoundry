import os

from pyfakefs import fake_filesystem_unittest

from shellfoundry.utilities.shell_package_builder import ShellPackageBuilder
from tests.asserts import assertFileExists
from tests.test_utilities.test_package_builder import TestPackageBuilder


class TestShellPackageBuilder(fake_filesystem_unittest.TestCase):
    def setUp(self):
        self.setUpPyfakefs()

    def test_tosca_based_shell_packed(self):
        # Arrange
        self.fs.CreateFile('nut-shell/TOSCA-Metadata/TOSCA.meta',
                           contents='TOSCA-Meta-File-Version: 1.0 '
                                    'CSAR-Version: 1.1 '
                                    'Created-By: Anonymous'
                                    'Entry-Definitions: shell-definition.yml')

        self.fs.CreateFile('nut-shell/shell-definition.yml',
                           contents='SOME SHELL DEFINITION')

        self.fs.CreateFile('nut-shell/shell-icon.png',
                           contents='IMAGE')

        os.chdir('nut-shell')

        command_executor = ShellPackageBuilder()

        # Act
        command_executor.pack()

        # Assert
        assertFileExists(self, 'dist/shell-package.zip')
        TestPackageBuilder.unzip('dist/shell-package.zip', 'dist/package_content')

        assertFileExists(self, 'dist/package_content/TOSCA-Metadata/TOSCA.meta')
        assertFileExists(self, 'dist/package_content/shell-definition.yml')
        assertFileExists(self, 'dist/package_content/shell-icon.png')
        assertFileExists(self, 'dist/package_content/shell-driver.zip')

