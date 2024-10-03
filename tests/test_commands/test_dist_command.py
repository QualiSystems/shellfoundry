#!/usr/bin/python
import os
import unittest
from unittest.mock import MagicMock, patch

from shellfoundry.commands.dist_command import DistCommandExecutor
from shellfoundry.models.install_config import InstallConfig


class TestDistCommandExecutor(unittest.TestCase):
    def setUp(self):
        self.mock_dependencies_packager = MagicMock()

    @patch("shellfoundry.commands.dist_command.Configuration")
    def test_dist(self, mock_configuration):
        mock_configuration.return_value.read.return_value = InstallConfig.get_default()
        command_executor = DistCommandExecutor(
            dependencies_packager=self.mock_dependencies_packager,
        )

        with patch.object(os, "getcwd", return_value="shell_path"):
            command_executor.dist(enable_cs_repo=True)
            self.mock_dependencies_packager.save_offline_dependencies.assert_called_with(  # noqa: E501
                "shell_path/src/requirements.txt",
                "shell_path/dist/offline_requirements",
                "localhost",
            )

            command_executor.dist(enable_cs_repo=False)
            self.mock_dependencies_packager.save_offline_dependencies.assert_called_with(  # noqa: E501
                "shell_path/src/requirements.txt",
                "shell_path/dist/offline_requirements",
                None,
            )
