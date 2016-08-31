from mock import patch, Mock
from pyfakefs import fake_filesystem_unittest
from shellfoundry.utilities.shell_package_installer import ShellPackageInstaller


class TestShellPackageInstaller(fake_filesystem_unittest.TestCase):
    def setUp(self):
        self.setUpPyfakefs()

    @patch('shellfoundry.utilities.shell_package_installer.CloudShellRestApiClient')
    def test_install_shell_updates_an_existing_shell(self, rest_client_mock):
        # Arrange
        mock_client = Mock()
        rest_client_mock.return_value = mock_client
        installer = ShellPackageInstaller()

        # Act
        installer.install('work/nut-shell')

        # Assert
        self.assertTrue(mock_client.update_shell.called)

    @patch('shellfoundry.utilities.shell_package_installer.CloudShellRestApiClient')
    def test_install_shell_adds_a_new_shell_when_update_fails(self, rest_client_mock):
        # Arrange
        mock_client = Mock()
        mock_client.update_shell = Mock(side_effect=Exception())
        rest_client_mock.return_value = mock_client
        installer = ShellPackageInstaller()

        # Act
        installer.install('work/nut-shell')

        # Assert
        self.assertTrue(mock_client.update_shell.called)
        self.assertTrue(mock_client.add_shell.called)
