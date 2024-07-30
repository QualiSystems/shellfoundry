#!/usr/bin/python
import unittest
from unittest.mock import MagicMock, patch

from click import BadParameter, ClickException
from cloudshell.rest.api import FeatureUnavailable

from shellfoundry import ALTERNATIVE_STANDARDS_PATH
from shellfoundry.commands.new_command import NewCommandExecutor
from shellfoundry.models.install_config import InstallConfig


class TestNewCommandExecutor(unittest.TestCase):
    def setUp(self):
        self.default_config = InstallConfig.get_default()
        self.mock_template_compiler = MagicMock()
        self.mock_template_retriever = MagicMock()
        self.mock_repository_downloader = MagicMock()
        self.mock_standards = MagicMock()
        self.mock_standard_versions = MagicMock()
        self.mock_shell_name_validations = MagicMock()

    @patch("shellfoundry.commands.new_command.os")
    @patch("shellfoundry.commands.new_command.click.echo")
    def test_new_wrong_shell_name(self, mock_echo, mock_os):
        self.mock_shell_name_validations.validate_shell_name.return_value = False

        command_executor = NewCommandExecutor(
            template_compiler=self.mock_template_compiler,
            template_retriever=self.mock_template_retriever,
            repository_downloader=self.mock_repository_downloader,
            standards=self.mock_standards,
            standard_versions=self.mock_standard_versions,
            shell_name_validations=self.mock_shell_name_validations,
        )

        with self.assertRaisesRegex(
            BadParameter, "Shell name must begin with a letter"
        ):
            command_executor.new(
                name="_Shell_Name",
                template="shell/template",
                version="template_version",
                python_version="python_version",
            )
            mock_echo.assert_not_called()

    @patch("shellfoundry.commands.new_command.os")
    @patch("shellfoundry.commands.new_command.click.echo")
    def test_new_standard_fetch_base_exception(self, mock_echo, mock_os):
        exc_msg = "Some base exception"
        self.mock_shell_name_validations.validate_shell_name.return_value = True
        self.mock_standards.fetch = MagicMock(
            side_effect=Exception(exc_msg),
        )

        command_executor = NewCommandExecutor(
            template_compiler=self.mock_template_compiler,
            template_retriever=self.mock_template_retriever,
            repository_downloader=self.mock_repository_downloader,
            standards=self.mock_standards,
            standard_versions=self.mock_standard_versions,
            shell_name_validations=self.mock_shell_name_validations,
        )

        with self.assertRaisesRegex(
            ClickException, f"Cannot retrieve standards list. Error: {exc_msg}"
        ):
            command_executor.new(
                name="Shell_Name",
                template="shell/template",
                version="template_version",
                python_version="python_version",
            )
            self.mock_standards.fetch.assert_called_once_with()
            mock_echo.assert_not_called()

    @patch("shellfoundry.commands.new_command.os")
    @patch("shellfoundry.commands.new_command.click.echo")
    def test_new_standard_fetch_unavailable_and_base_exception(
        self, mock_echo, mock_os
    ):
        exc_msg = "Some base exception"
        self.mock_shell_name_validations.validate_shell_name.return_value = True
        self.mock_standards.fetch = MagicMock(
            side_effect=[FeatureUnavailable, Exception(exc_msg)]
        )

        command_executor = NewCommandExecutor(
            template_compiler=self.mock_template_compiler,
            template_retriever=self.mock_template_retriever,
            repository_downloader=self.mock_repository_downloader,
            standards=self.mock_standards,
            standard_versions=self.mock_standard_versions,
            shell_name_validations=self.mock_shell_name_validations,
        )

        with self.assertRaisesRegex(BaseException, exc_msg):
            command_executor.new(name="_Shell_Name", template="shell/template")
            self.mock_standards.fetch.assert_called_with()
            self.mock_standards.fetch.assert_called_with(
                alternative=ALTERNATIVE_STANDARDS_PATH
            )
            mock_echo.assert_not_called()

    @patch("shellfoundry.commands.new_command.os")
    @patch("shellfoundry.commands.new_command.click.echo")
    @patch(
        "shellfoundry.commands.new_command.NewCommandExecutor._is_direct_online_template",  # noqa: E501
        return_value=True,
    )
    @patch(
        "shellfoundry.commands.new_command.NewCommandExecutor._import_direct_online_template"  # noqa: E501
    )
    def test_new_direct_online_template(
        self, mock_import, mock_direct_online, mock_echo, mock_os
    ):
        self.mock_shell_name_validations.validate_shell_name.return_value = True
        self.mock_standards.fetch.return_value = {"resource": ["1.0.0", "1.0.1"]}

        command_executor = NewCommandExecutor(
            template_compiler=self.mock_template_compiler,
            template_retriever=self.mock_template_retriever,
            repository_downloader=self.mock_repository_downloader,
            standards=self.mock_standards,
            standard_versions=self.mock_standard_versions,
            shell_name_validations=self.mock_shell_name_validations,
        )

        command_executor.new(
            name="Shell_Name",
            template="shell/template",
            version="template_version",
            python_version="python_version",
        )

        mock_import.assert_called_once_with(
            "Shell_Name",
            False,
            "shell/template",
            {"resource": ["1.0.0", "1.0.1"]},
            "python_version",
        )
        mock_echo.assert_called_with(
            "Created shell {} based on template {}".format(
                "Shell_Name", "shell/template"
            )
        )

    @patch("shellfoundry.commands.new_command.os")
    @patch("shellfoundry.commands.new_command.click.echo")
    @patch(
        "shellfoundry.commands.new_command.NewCommandExecutor._is_direct_online_template",  # noqa: E501
        return_value=False,
    )
    @patch(
        "shellfoundry.commands.new_command.NewCommandExecutor._is_direct_local_template",  # noqa: E501
        return_value=True,
    )
    @patch(
        "shellfoundry.commands.new_command.NewCommandExecutor._import_local_template"
    )
    def test_new_direct_local_template(
        self, mock_import, mock_direct_local, mock_online_local, mock_echo, mock_os
    ):
        self.mock_shell_name_validations.validate_shell_name.return_value = True
        self.mock_standards.fetch.return_value = {"resource": ["1.0.0", "1.0.1"]}

        command_executor = NewCommandExecutor(
            template_compiler=self.mock_template_compiler,
            template_retriever=self.mock_template_retriever,
            repository_downloader=self.mock_repository_downloader,
            standards=self.mock_standards,
            standard_versions=self.mock_standard_versions,
            shell_name_validations=self.mock_shell_name_validations,
        )

        command_executor.new(
            name="Shell_Name",
            template="shell/template",
            version="template_version",
            python_version="python_version",
        )

        mock_import.assert_called_once_with(
            "Shell_Name",
            False,
            "shell/template",
            {"resource": ["1.0.0", "1.0.1"]},
            "python_version",
        )
        mock_echo.assert_called_with(
            "Created shell {} based on template {}".format(
                "Shell_Name", "shell/template"
            )
        )

    @patch("shellfoundry.commands.new_command.os")
    @patch("shellfoundry.commands.new_command.click.echo")
    @patch(
        "shellfoundry.commands.new_command.NewCommandExecutor._is_direct_online_template",  # noqa: E501
        return_value=False,
    )
    @patch(
        "shellfoundry.commands.new_command.NewCommandExecutor._is_direct_local_template",  # noqa: E501
        return_value=False,
    )
    @patch("shellfoundry.commands.new_command.Configuration")
    @patch(
        "shellfoundry.commands.new_command.NewCommandExecutor._import_online_template"
    )
    def test_new_github_templates(
        self,
        mock_import,
        mock_configuration,
        mock_direct_local,
        mock_online_local,
        mock_echo,
        mock_os,
    ):
        self.mock_shell_name_validations.validate_shell_name.return_value = True
        self.mock_standards.fetch.return_value = {"resource": ["1.0.0", "1.0.1"]}
        mock_configuration.return_value.read.return_value = self.default_config

        command_executor = NewCommandExecutor(
            template_compiler=self.mock_template_compiler,
            template_retriever=self.mock_template_retriever,
            repository_downloader=self.mock_repository_downloader,
            standards=self.mock_standards,
            standard_versions=self.mock_standard_versions,
            shell_name_validations=self.mock_shell_name_validations,
        )

        command_executor.new(
            name="Shell_Name",
            template="shell/template",
            version="template_version",
            python_version="python_version",
        )

        mock_import.assert_called_once_with(
            "Shell_Name",
            False,
            "shell/template",
            "template_version",
            {"resource": ["1.0.0", "1.0.1"]},
            "python_version",
        )
        mock_echo.assert_called_with(
            "Created shell {} based on template {}".format(
                "Shell_Name", "shell/template"
            )
        )

    @patch("shellfoundry.commands.new_command.os")
    @patch("shellfoundry.commands.new_command.click.echo")
    @patch(
        "shellfoundry.commands.new_command.NewCommandExecutor._is_direct_online_template",  # noqa: E501
        return_value=False,
    )
    @patch(
        "shellfoundry.commands.new_command.NewCommandExecutor._is_direct_local_template",  # noqa: E501
        return_value=False,
    )
    @patch(
        "shellfoundry.commands.new_command.NewCommandExecutor._get_local_template_full_path",  # noqa: E501
        return_value="local_template_name",
    )
    @patch("shellfoundry.commands.new_command.Configuration")
    @patch(
        "shellfoundry.commands.new_command.NewCommandExecutor._import_local_template"
    )
    def test_new_local_templates(
        self,
        mock_import,
        mock_configuration,
        mock_get_template,
        mock_direct_local,
        mock_online_local,
        mock_echo,
        mock_os,
    ):
        self.mock_shell_name_validations.validate_shell_name.return_value = True
        self.mock_standards.fetch.return_value = {"resource": ["1.0.0", "1.0.1"]}
        self.default_config.online_mode = "False"
        mock_configuration.return_value.read.return_value = self.default_config

        command_executor = NewCommandExecutor(
            template_compiler=self.mock_template_compiler,
            template_retriever=self.mock_template_retriever,
            repository_downloader=self.mock_repository_downloader,
            standards=self.mock_standards,
            standard_versions=self.mock_standard_versions,
            shell_name_validations=self.mock_shell_name_validations,
        )

        command_executor.new(
            name="Shell_Name",
            template="shell/template",
            version="template_version",
            python_version="python_version",
        )

        mock_import.assert_called_once_with(
            "Shell_Name",
            False,
            "local_template_name",
            {"resource": ["1.0.0", "1.0.1"]},
            "python_version",
        )
        mock_echo.assert_called_with(
            "Created shell {} based on template {}".format(
                "Shell_Name", "local_template_name"
            )
        )

    @patch("shellfoundry.commands.new_command.os")
    @patch("shellfoundry.commands.new_command.click.echo")
    @patch("shellfoundry.commands.new_command.click.secho")
    @patch(
        "shellfoundry.commands.new_command.NewCommandExecutor._is_direct_online_template",  # noqa: E501
        return_value=False,
    )
    @patch(
        "shellfoundry.commands.new_command.NewCommandExecutor._is_direct_local_template",  # noqa: E501
        return_value=False,
    )
    @patch(
        "shellfoundry.commands.new_command.NewCommandExecutor._get_local_template_full_path",  # noqa: E501
        return_value=NewCommandExecutor.L1_TEMPLATE,
    )
    @patch("shellfoundry.commands.new_command.Configuration")
    @patch(
        "shellfoundry.commands.new_command.NewCommandExecutor._import_local_template"
    )
    def test_new_l1_template(
        self,
        mock_import,
        mock_configuration,
        mock_get_template,
        mock_direct_local,
        mock_online_local,
        mock_secho,
        mock_echo,
        mock_os,
    ):
        self.mock_shell_name_validations.validate_shell_name.return_value = True
        self.mock_standards.fetch.return_value = {"resource": ["1.0.0", "1.0.1"]}
        self.default_config.online_mode = "False"
        mock_configuration.return_value.read.return_value = self.default_config

        command_executor = NewCommandExecutor(
            template_compiler=self.mock_template_compiler,
            template_retriever=self.mock_template_retriever,
            repository_downloader=self.mock_repository_downloader,
            standards=self.mock_standards,
            standard_versions=self.mock_standard_versions,
            shell_name_validations=self.mock_shell_name_validations,
        )

        command_executor.new(
            name="Shell_Name",
            template="shell/template",
            version="template_version",
            python_version="python_version",
        )

        mock_import.assert_called_once_with(
            "Shell_Name",
            False,
            command_executor.L1_TEMPLATE,
            {"resource": ["1.0.0", "1.0.1"]},
            "python_version",
        )
        mock_secho.assert_called_with(
            "WARNING: L1 shells support python 2.7 only!", fg="yellow"
        )
        mock_echo.assert_called_with(
            "Created shell {} based on template {}".format(
                "Shell_Name", command_executor.L1_TEMPLATE
            )
        )
