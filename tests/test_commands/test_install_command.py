from __future__ import annotations

import unittest
from unittest.mock import MagicMock, patch
from urllib.error import HTTPError, URLError

from shellfoundry.commands.install_command import InstallCommandExecutor
from shellfoundry.exceptions import FatalError


class TestInstallCommandExecutor(unittest.TestCase):
    def setUp(self):
        self.mock_cloudshell_config_reader = MagicMock()
        self.mock_installer = MagicMock()
        self.mock_shell_config_reader = MagicMock()
        self.mock_shell_package_installer = MagicMock()

    @patch("shellfoundry.commands.install_command.ShellPackage")
    @patch("shellfoundry.commands.install_command.os")
    @patch("shellfoundry.commands.install_command.click.secho")
    def test_install_layer_one(self, secho_mock, os_mock, shell_package_mock):
        shell_package_mock.return_value.is_layer_one.return_value = True

        command_executor = InstallCommandExecutor(
            cloudshell_config_reader=self.mock_cloudshell_config_reader,
            installer=self.mock_installer,
            shell_config_reader=self.mock_shell_config_reader,
            shell_package_installer=self.mock_shell_package_installer,
        )

        # Act
        command_executor.install()

        # Assert
        secho_mock.assert_any_call(
            "Installing a L1 shell directly via shellfoundry is not supported. "
            "Please follow the L1 shell import procedure described in help.quali.com.",
            fg="yellow",
        )

    @patch("shellfoundry.commands.install_command.ShellPackage")
    @patch("shellfoundry.commands.install_command.os")
    @patch("shellfoundry.commands.install_command.click.secho")
    def test_install_gen2_shell_success(self, secho_mock, os_mock, shell_package_mock):
        shell_package_mock.return_value.is_layer_one.return_value = False
        shell_package_mock.return_value.is_tosca.return_value = True
        os_mock.getcwd.return_value = "current path"

        command_executor = InstallCommandExecutor(
            cloudshell_config_reader=self.mock_cloudshell_config_reader,
            installer=self.mock_installer,
            shell_config_reader=self.mock_shell_config_reader,
            shell_package_installer=self.mock_shell_package_installer,
        )

        # Act
        command_executor.install()

        # Assert
        self.mock_shell_package_installer.install.assert_called_once_with(
            "current path"
        )
        secho_mock.assert_any_call("Successfully installed shell", fg="green")

    @patch("shellfoundry.commands.install_command.ShellPackage")
    @patch("shellfoundry.commands.install_command.os")
    @patch("shellfoundry.commands.install_command.click.secho")
    def test_install_gen1_shell_success(self, secho_mock, os_mock, shell_package_mock):
        shell_package_mock.return_value.is_layer_one.return_value = False
        shell_package_mock.return_value.is_tosca.return_value = False

        command_executor = InstallCommandExecutor(
            cloudshell_config_reader=self.mock_cloudshell_config_reader,
            installer=self.mock_installer,
            shell_config_reader=self.mock_shell_config_reader,
            shell_package_installer=self.mock_shell_package_installer,
        )

        # Act
        command_executor.install()

        # Assert
        self.mock_installer.install.assert_called_once()
        secho_mock.assert_any_call("Successfully installed shell", fg="green")

    @patch("shellfoundry.commands.install_command.ShellPackage")
    @patch("shellfoundry.commands.install_command.os")
    def test_install_gen1_shell_cs_connection_failed(self, os_mock, shell_package_mock):
        shell_package_mock.return_value.is_layer_one.return_value = False
        shell_package_mock.return_value.is_tosca.return_value = False
        self.mock_installer.install = MagicMock(side_effect=URLError("Error reason"))

        command_executor = InstallCommandExecutor(
            cloudshell_config_reader=self.mock_cloudshell_config_reader,
            installer=self.mock_installer,
            shell_config_reader=self.mock_shell_config_reader,
            shell_package_installer=self.mock_shell_package_installer,
        )

        # Act
        with self.assertRaises(FatalError) as context:
            command_executor.install()

        # Assert
        self.mock_installer.install.assert_called_once()
        self.assertTrue(
            str(context.exception) == "Connection to CloudShell Server failed. "
            "Please make sure it is up and running properly."
        )

    @patch("shellfoundry.commands.install_command.ShellPackage")
    @patch("shellfoundry.commands.install_command.os")
    def test_install_gen1_shell_cs_login_failed(self, os_mock, shell_package_mock):
        shell_package_mock.return_value.is_layer_one.return_value = False
        shell_package_mock.return_value.is_tosca.return_value = False
        self.mock_installer.install = MagicMock(
            side_effect=HTTPError("", 401, "Login Failed", None, None)
        )

        command_executor = InstallCommandExecutor(
            cloudshell_config_reader=self.mock_cloudshell_config_reader,
            installer=self.mock_installer,
            shell_config_reader=self.mock_shell_config_reader,
            shell_package_installer=self.mock_shell_package_installer,
        )

        # Act
        with self.assertRaises(FatalError) as context:
            command_executor.install()

        # Assert
        self.mock_installer.install.assert_called_once()
        self.assertTrue(
            str(context.exception)
            == "Login to CloudShell failed. Please verify the credentials in the config"  # noqa: E501
        )

    @patch("shellfoundry.commands.install_command.ShellPackage")
    @patch("shellfoundry.commands.install_command.os")
    def test_install_gen1_shell_non_auth_http_error(self, os_mock, shell_package_mock):
        shell_package_mock.return_value.is_layer_one.return_value = False
        shell_package_mock.return_value.is_tosca.return_value = False
        self.mock_installer.install = MagicMock(
            side_effect=HTTPError("", 404, "Non auth error", None, None)
        )

        command_executor = InstallCommandExecutor(
            cloudshell_config_reader=self.mock_cloudshell_config_reader,
            installer=self.mock_installer,
            shell_config_reader=self.mock_shell_config_reader,
            shell_package_installer=self.mock_shell_package_installer,
        )

        # Act
        with self.assertRaises(FatalError) as context:
            command_executor.install()

        # Assert
        self.mock_installer.install.assert_called_once()
        self.assertTrue(
            str(context.exception) == "Failed to install shell. "
            "CloudShell responded with: 'HTTP Error 404: Non auth error'"
        )

    @patch("shellfoundry.commands.install_command.ShellPackage")
    @patch("shellfoundry.commands.install_command.os")
    def test_install_gen1_shell_base_exception(self, os_mock, shell_package_mock):
        shell_package_mock.return_value.is_layer_one.return_value = False
        shell_package_mock.return_value.is_tosca.return_value = False
        self.mock_installer.install = MagicMock(
            side_effect=Exception("Some base exception")
        )

        command_executor = InstallCommandExecutor(
            cloudshell_config_reader=self.mock_cloudshell_config_reader,
            installer=self.mock_installer,
            shell_config_reader=self.mock_shell_config_reader,
            shell_package_installer=self.mock_shell_package_installer,
        )

        # Act
        with self.assertRaises(FatalError) as context:
            command_executor.install()

        # Assert
        self.mock_installer.install.assert_called_once()
        self.assertTrue(
            str(context.exception) == "Failed to install shell. "
            "CloudShell responded with: 'Some base exception'"
        )
