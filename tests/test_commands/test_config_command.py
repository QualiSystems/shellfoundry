#!/usr/bin/python

import os
from unittest.mock import MagicMock, patch

from click import BadArgumentUsage
from pyfakefs import fake_filesystem_unittest

from shellfoundry.commands.config_command import DEFAULTS_CHAR, ConfigCommandExecutor


class TestConfigCommandExecutor(fake_filesystem_unittest.TestCase):
    def setUp(self):
        self.setUpPyfakefs()

    @patch("shellfoundry.utilities.config.config_providers.click.get_app_dir")
    @patch("shellfoundry.commands.config_command.click.echo")
    @patch(
        "shellfoundry.commands.config_command.ConfigCommandExecutor._format_config_as_table"  # noqa: E501
    )
    def test_get_all_config_keys(self, mock_format_config, echo_mock, get_app_dir_mock):
        # Arrange
        self.fs.create_file(
            "/quali/shellfoundry/global_config.yml",
            contents="""
install:
  key: value
not_supported_section:
  no_key: no_value
    """,
        )
        get_app_dir_mock.return_value = "/quali/shellfoundry"

        # Act
        ConfigCommandExecutor(True).config()

        # Assert
        mock_format_config.assert_called_once_with(
            {
                "install": {
                    "github_login": " *",
                    "author": "Anonymous *",
                    "online_mode": "True *",
                    "username": "admin *",
                    "domain": "Global *",
                    "port": "9000 *",
                    "host": "localhost *",
                    "github_password": "gh_pass *",
                    "template_location": "Empty *",
                    "password": "admin *",
                    "defaultview": "gen2 *",
                    "key": "value",
                }
            },
            DEFAULTS_CHAR,
        )

    @patch("shellfoundry.utilities.config.config_providers.click.get_app_dir")
    @patch("shellfoundry.commands.config_command.click.echo")
    def test_set_global_config_key(self, echo_mock, get_app_dir_mock):
        # Arrange
        self.fs.create_file(
            "/quali/shellfoundry/global_config.yml",
            contents="""
install:
  key: value""",
        )
        get_app_dir_mock.return_value = "/quali/shellfoundry"

        # Act
        ConfigCommandExecutor(True).config(("new_key", "new_value"))

        # Assert
        echo_mock.assert_called_once_with("new_key: new_value was saved successfully")
        desired_result = """install:
  key: value
  new_key: new_value
"""
        self.assertTrue(
            self.fs.get_object("/quali/shellfoundry/global_config.yml").contents
            == desired_result
        )

    @patch("shellfoundry.utilities.config.config_providers.os.getcwd")
    @patch("shellfoundry.commands.config_command.click.echo")
    def test_set_local_config_key(self, echo_mock, getcwd_mock):
        # Arrange
        self.fs.create_file(
            "/current_shell/cloudshell_config.yml",
            contents="""
install:
  key: value""",
        )
        getcwd_mock.return_value = "/current_shell"
        # Act
        ConfigCommandExecutor(False).config(("new_key", "new_value"))

        # Assert
        echo_mock.assert_called_with("new_key: new_value was saved successfully")
        desired_result = """install:
  key: value
  new_key: new_value
"""
        self.assertTrue(
            self.fs.get_object("/current_shell/cloudshell_config.yml").contents
            == desired_result
        )

    @patch("shellfoundry.utilities.config.config_providers.click.get_app_dir")
    @patch("shellfoundry.commands.config_command.click.echo")
    @patch(
        "shellfoundry.commands.config_command.ConfigCommandExecutor._format_config_as_table"  # noqa: E501
    )
    def test_get_all_config_keys_that_has_password_param(
        self, mock_format_config, echo_mock, get_app_dir_mock
    ):
        # Arrange
        self.fs.create_file(
            "/quali/shellfoundry/global_config.yml",
            contents="""
install:
  key: value
  password: aabcdefs
  yetanotherkey: yetanothervalue""",
        )
        get_app_dir_mock.return_value = "/quali/shellfoundry"

        # Act
        ConfigCommandExecutor(True).config()

        # Assert
        mock_format_config.assert_called_once_with(
            {
                "install": {
                    "password": "aabcdefs",
                    "username": "admin *",
                    "host": "localhost *",
                    "author": "Anonymous *",
                    "online_mode": "True *",
                    "template_location": "Empty *",
                    "domain": "Global *",
                    "github_login": " *",
                    "port": "9000 *",
                    "github_password": "gh_pass *",
                    "defaultview": "gen2 *",
                    "key": "value",
                    "yetanotherkey": "yetanothervalue",
                }
            },
            DEFAULTS_CHAR,
        )

    @patch("shellfoundry.utilities.config.config_providers.click.get_app_dir")
    @patch("shellfoundry.commands.config_command.click.echo")
    def test_remove_key_is_allowed(self, echo_mock, get_app_dir_mock):
        # Arrange
        self.fs.create_file(
            "/quali/shellfoundry/global_config.yml",
            contents="""
install:
  key: value
  yetanotherkey: yetanothervalue""",
        )
        get_app_dir_mock.return_value = "/quali/shellfoundry"
        key = "yetanotherkey"

        # Act
        ConfigCommandExecutor(True).config(key_to_remove=key)

        # Assert
        echo_mock.assert_called_once_with("yetanotherkey was deleted successfully")
        desired_result = """install:
  key: value
"""
        file_content = self.fs.get_object(
            "/quali/shellfoundry/global_config.yml"
        ).contents
        self.assertTrue(
            file_content == desired_result,
            f"Expected: {desired_result}{os.linesep}Actual: {file_content}",
        )

    @patch("shellfoundry.utilities.config.config_providers.click.get_app_dir")
    @patch("shellfoundry.commands.config_command.click.echo")
    def test_remove_key_from_global_where_global_config_file_does_not_exists(
        self, echo_mock, get_app_dir_mock
    ):
        # Arrange
        get_app_dir_mock.return_value = "/quali/shellfoundry"
        key = "yetanotherkey"

        # Act
        ConfigCommandExecutor(True).config(key_to_remove=key)

        # Assert
        echo_mock.assert_called_with("Failed to delete key")

    @patch("shellfoundry.utilities.config.config_providers.click.get_app_dir")
    @patch("shellfoundry.commands.config_command.click.echo")
    def test_update_existing_key(self, echo_mock, get_app_dir_mock):
        # Arrange
        self.fs.create_file(
            "/quali/shellfoundry/global_config.yml",
            contents="""
install:
  key: value""",
        )
        get_app_dir_mock.return_value = "/quali/shellfoundry"

        # Act
        ConfigCommandExecutor(True).config(("key", "new_value"))

        # Assert
        echo_mock.assert_called_once_with("key: new_value was saved successfully")
        desired_result = """install:
  key: new_value
"""
        file_content = self.fs.get_object(
            "/quali/shellfoundry/global_config.yml"
        ).contents
        self.assertTrue(
            file_content == desired_result,
            f"Expected: {desired_result}{os.linesep}Actual: {file_content}",
        )

    @patch("shellfoundry.utilities.config.config_providers.click.get_app_dir")
    @patch("shellfoundry.commands.config_command.click.echo")
    def test_adding_key_to_global_config_that_hasnt_been_created_yet(
        self, echo_mock, get_app_dir_mock
    ):
        # Arrange
        get_app_dir_mock.return_value = "/quali/shellfoundry"

        # Act
        ConfigCommandExecutor(True).config(("key", "new_value"))

        # Assert
        echo_mock.assert_called_with("key: new_value was saved successfully")
        desired_result = """install:
  key: new_value
"""
        file_content = self.fs.get_object(
            "/quali/shellfoundry/global_config.yml"
        ).contents
        self.assertTrue(
            file_content == desired_result,
            f"Expected: {desired_result}{os.linesep}Actual: {file_content}",
        )

    @patch("shellfoundry.utilities.config.config_providers.click.get_app_dir")
    @patch("shellfoundry.commands.config_command.click.echo")
    def test_adding_key_to_global_config_with_empty_value(
        self, echo_mock, get_app_dir_mock
    ):
        # Arrange
        get_app_dir_mock.return_value = "/quali/shellfoundry"

        with self.assertRaisesRegex(BadArgumentUsage, "Field '.+' can not be empty"):
            ConfigCommandExecutor(True).config(("key", ""))

    @patch("shellfoundry.utilities.config.config_providers.click.get_app_dir")
    @patch("platform.node", MagicMock(return_value="machine-name-here"))
    def test_set_password_config_password_should_appear_encrypted(
        self, get_app_dir_mock
    ):
        # Arrange
        self.fs.create_file(
            "/quali/shellfoundry/global_config.yml",
            contents="""
install:
  key: value
""",
        )
        get_app_dir_mock.return_value = "/quali/shellfoundry"

        # Act
        ConfigCommandExecutor(True).config(("password", "admin"))

        # Assert
        desired_result = """install:
  key: value
  password: DAUOAQc=
"""
        file_content = self.fs.get_object(
            "/quali/shellfoundry/global_config.yml"
        ).contents
        self.assertTrue(
            file_content == desired_result,
            f"Expected: {desired_result}{os.linesep}Actual: {file_content}",
        )
