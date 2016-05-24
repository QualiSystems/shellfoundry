import os
import unittest
from mock import Mock, patch, MagicMock
from pyfakefs import fake_filesystem_unittest
from shellfoundry.commands.install_command import InstallCommandExecutor
from shellfoundry.models.install_config import InstallConfig


class TestInstallCommandExecutor(fake_filesystem_unittest.TestCase):
    def setUp(self):
        self.setUpPyfakefs()

    def test_when_config_files_exist_install_succeeds(self):
        # Arrange
        self.fs.CreateFile('nut_shell/shell.yml', contents="""
shell:
    name: nut_shell
    """)
        self.fs.CreateFile('nut_shell/cloudshell_config.yml', contents="""
install:
    host: localhost
    port: 9000
    username: YOUR_USERNAME
    password: YOUR_PASSWORD
    domain: Global
    """)
        os.chdir('nut_shell')

        mock_installer = MagicMock()
        command_executor = InstallCommandExecutor(installer=mock_installer)

        # Act
        command_executor.install()

        # Assert
        mock_installer.install.assert_called_once_with('nut_shell', InstallConfig('localhost', 9000, 'YOUR_USERNAME',
                                                                                  'YOUR_PASSWORD', 'Global'))

