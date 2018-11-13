import os

from urllib2 import HTTPError, URLError
from mock import Mock, patch, MagicMock, call
from pyfakefs import fake_filesystem_unittest

from shellfoundry.commands.install_command import InstallCommandExecutor
from shellfoundry.models.install_config import InstallConfig
from shellfoundry.exceptions import FatalError

LOGIN_ERROR_MESSAGE = 'Login failed for user: YOUR_USERNAME. Please make sure the username and password are correct.'


class TestInstallCommandExecutor(fake_filesystem_unittest.TestCase):
    def setUp(self):
        self.setUpPyfakefs()

    @patch('click.secho')
    def test_when_config_files_exist_install_succeeds(self, secho_mock):
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
    author: AUTHOR
    online_mode: ONLINE_MODE
    template_location: TEMPLATE_LOCATION
    """)
        os.chdir('nut_shell')

        mock_installer = MagicMock()
        command_executor = InstallCommandExecutor(installer=mock_installer)

        # Act
        command_executor.install()

        # Assert
        mock_installer.install.assert_called_once_with('nut_shell', InstallConfig('localhost', 9000, 'YOUR_USERNAME',
                                                                                  'YOUR_PASSWORD', 'Global', "AUTHOR",
                                                                                  'ONLINE_MODE', 'TEMPLATE_LOCATION'))
        secho_mock.assert_any_call('Successfully installed shell', fg='green')

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

    @patch('click.secho')
    def test_install_layer_one_shell(self, secho_mock):
        # Arrange
        self.fs.CreateFile('cloudshell-L1-test/datamodel/datamodel.xml')
        os.chdir('cloudshell-L1-test')

        mock_shell_package_installer = MagicMock()
        command_executor = InstallCommandExecutor(shell_package_installer=mock_shell_package_installer)

        # Act
        command_executor.install()

        # Assert
        secho_mock.assert_any_call("Installing a L1 shell directly via shellfoundry is not supported. "
                                   "Please follow the L1 shell import procedure described in help.quali.com.",
                                   fg="yellow")

    def test_proper_error_message_displayed_when_login_failed(self):
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
        mock_installer.install = Mock(side_effect=HTTPError('', 401, LOGIN_ERROR_MESSAGE, None, None))
        command_executor = InstallCommandExecutor(installer=mock_installer)

        # Act
        with self.assertRaises(FatalError) as context:
            command_executor.install()

        # Assert
        self.assertTrue(str(context.exception) ==
                        u'Login to CloudShell failed. Please verify the credentials in the config')

    def test_proper_error_message_when_non_authentication_http_error_raised(self):
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
        mock_installer.install = Mock(side_effect=HTTPError('', 404, LOGIN_ERROR_MESSAGE, None, None))
        command_executor = InstallCommandExecutor(installer=mock_installer)

        # Act
        with self.assertRaises(FatalError) as context:
            command_executor.install()

        # Assert
        self.assertTrue(str(context.exception) == u"Failed to install shell. CloudShell responded with: '{}'"
                        .format('Login failed for user: YOUR_USERNAME. '
                                'Please make sure the username and password are correct.'),
                        "Actual: {}".format(context.exception))

    def test_proper_error_appears_when_connection_to_cs_failed(self):
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
        mock_installer.install = Mock(side_effect=URLError(''))
        command_executor = InstallCommandExecutor(installer=mock_installer)

        # Act
        with self.assertRaises(FatalError) as context:
            command_executor.install()

        # Assert
        self.assertTrue(
            context.exception.message == u'Connection to CloudShell Server failed. Please make sure it is up and running properly.')

    def test_proper_error_appears_when_old_shell_installation_fails(self):
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
        ex_msg = 'Quali Error: some fancy error here'
        mock_installer.install = Mock(side_effect=Exception(ex_msg))
        command_executor = InstallCommandExecutor(installer=mock_installer)

        # Act
        with self.assertRaises(FatalError) as context:
            command_executor.install()

        # Assert
        self.assertTrue(
            context.exception.message == u"Failed to install shell. CloudShell responded with: '{}'".format(ex_msg))
