import shellfoundry.utilities.shell_package_installer as spi

from urllib2 import HTTPError
from cloudshell.rest.exceptions import ShellNotFoundException
from mock import patch, Mock
from pyfakefs import fake_filesystem_unittest
from shellfoundry.utilities.shell_package_installer import ShellPackageInstaller
from shellfoundry.exceptions import FatalError
from cloudshell.rest.api import PackagingRestApiClient


def mock_rest_client(update_side_effect, add_side_effect):
    mock_client = Mock()
    mock_client.update_shell = Mock(side_effect=update_side_effect)
    mock_client.add_shell = Mock(side_effect=add_side_effect)
    return mock_client


def add_shell_error_message(err_msg):
    return ("\n"
            "    {\n"
            "        \"Message\" : \"" + err_msg + "\"\n"
                                                   "    }\n")


class TestShellPackageInstaller(fake_filesystem_unittest.TestCase):
    def setUp(self):
        self.setUpPyfakefs()

    @patch('shellfoundry.utilities.shell_package_installer.PackagingRestApiClient')
    def test_install_shell_updates_an_existing_shell(self, rest_client_mock):
        # Arrange
        mock_client = Mock()
        rest_client_mock.return_value = mock_client
        installer = ShellPackageInstaller()

        # Act
        with patch('click.echo'):
            installer.install('work/nut-shell')

        # Assert
        self.assertTrue(mock_client.update_shell.called)

    @patch('shellfoundry.utilities.shell_package_installer.PackagingRestApiClient')
    def test_install_shell_adds_a_new_shell_when_shell_does_not_exist(self, rest_client_mock):
        # Arrange
        mock_client = Mock()
        mock_client.update_shell = Mock(side_effect=ShellNotFoundException())
        rest_client_mock.return_value = mock_client
        installer = ShellPackageInstaller()

        # Act
        with patch('click.echo'):
            installer.install('work/nut-shell')

        # Assert
        self.assertTrue(mock_client.update_shell.called)
        self.assertTrue(mock_client.add_shell.called)

    @patch('shellfoundry.utilities.shell_package_installer.PackagingRestApiClient')
    def test_shell_add_should_not_be_called_when_update_fails(self, rest_client_mock):
        # Arrange
        mock_client = Mock()
        mock_client.update_shell = Mock(side_effect=Exception())
        rest_client_mock.return_value = mock_client
        installer = ShellPackageInstaller()

        # noinspection PyBroadException
        try:
            # Act
            with patch('click.echo'):
                installer.install('work/nut-shell')
        except Exception:
            pass

        # Assert
        self.assertTrue(mock_client.update_shell.called)
        self.assertFalse(mock_client.add_shell.called)

    @patch('shellfoundry.utilities.shell_package_installer.PackagingRestApiClient', new=Mock(side_effect=Exception()))
    def test_fail_to_open_connection_to_cs(self):
        # Arrange
        spi.CloudShell_Retry_Interval_Sec = 0  # doing that for test to run faster with no sleeps between connection failures
        installer = ShellPackageInstaller()

        with self.assertRaises(FatalError) as context:
            installer.install('work/nut-shell')

        # Assert
        self.assertTrue(
            context.exception.message == 'Connection to CloudShell Server failed. Please make sure it is up and running properly.')

    @patch('shellfoundry.utilities.shell_package_installer.PackagingRestApiClient',
           new=Mock(side_effect=HTTPError('', 401, '', None, None)))
    def test_fail_to_login_into_cs(self):
        # Arrange
        spi.CloudShell_Retry_Interval_Sec = 0  # doing that for test to run faster with no sleeps between connection failures
        installer = ShellPackageInstaller()

        with self.assertRaises(FatalError) as context:
            installer.install('work/nut-shell')

        # Assert
        self.assertTrue(
            context.exception.message == u'Login to CloudShell failed. Please verify the credentials in the config')

    @patch('shellfoundry.utilities.shell_package_installer.PackagingRestApiClient',
           new=Mock(side_effect=HTTPError('', 403, '', None, None)))
    def test_fail_with_http_error_other_than_authentication_error(self):
        # Arrange
        spi.CloudShell_Retry_Interval_Sec = 0  # doing that for test to run faster with no sleeps between connection failures
        installer = ShellPackageInstaller()

        with self.assertRaises(FatalError) as context:
            installer.install('work/nut-shell')

        # Assert
        self.assertTrue(
            context.exception.message == 'Connection to CloudShell Server failed. Please make sure it is up and running properly.')

    @patch('shellfoundry.utilities.shell_package_installer.PackagingRestApiClient', new=Mock(
        return_value=mock_rest_client(update_side_effect=ShellNotFoundException(),
                                      add_side_effect=Exception(add_shell_error_message('Failed to add shell')))))
    def test_fail_to_update_and_than_add_shell(self):
        # Arrange
        spi.Default_Time_Wait = 0  # doing that for test to run faster with no sleeps between connection failures
        installer = ShellPackageInstaller()

        # Act
        with self.assertRaises(FatalError) as context:
            installer.install('work/nut-shell')

        # Assert
        self.assertTrue(
            context.exception.message == "Failed to add new shell. CloudShell responded with: 'Failed to add shell'")
