import os
from urllib2 import HTTPError
from mock import Mock, patch, MagicMock
from pyfakefs import fake_filesystem_unittest
from shellfoundry.commands.install_command import InstallCommandExecutor
from shellfoundry.models.install_config import InstallConfig

LOGIN_ERROR_MESSAGE = 'Login failed for user: YOUR_USERNAME. Please make sure the username and password are correct.'


class TestInstallCommandExecutor(fake_filesystem_unittest.TestCase):
    def setUp(self):
        self.setUpPyfakefs()

    def test_when_config_files_exist_install_succeeds(self):
        # Arrange
        self.fs.CreateFile('nut_shell/shell.yml', contents="""
shell:
    name: nut_shell
    driver: NutShellDriver
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

    def test_tosca_based_shell_installed_when_tosca_meta_file_exists(self):
        # Arrange
        self.fs.CreateFile('nut-shell/TOSCA-Metadata/TOSCA.meta',
                           contents='TOSCA-Meta-File-Version: 1.0 \n'
                                    'CSAR-Version: 1.1 \n'
                                    'Created-By: Anonymous \n'
                                    'Entry-Definitions: shell-definition.yml')

        os.chdir('nut-shell')

        mock_shell_package_installer = MagicMock()
        command_executor = InstallCommandExecutor(shell_package_installer=mock_shell_package_installer)

        # Act
        command_executor.install()

        # Assert
        self.assertTrue(mock_shell_package_installer.install.called)

    @patch('click.echo')
    def test_proper_error_message_displayed_when_login_failed(self, echo_mock):
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
        mock_installer = Mock()
        mock_installer.install = Mock(side_effect=HTTPError('', '', LOGIN_ERROR_MESSAGE, None, None))
        command_executor = InstallCommandExecutor(installer=mock_installer)

        # Act
        command_executor.install()

        # Assert
        echo_mock.assert_called_once_with(u'Login to CloudShell failed. Please verify the credentials in cloudshell_config.yml')
