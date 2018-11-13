#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
from mock import patch
from pyfakefs import fake_filesystem_unittest

from shellfoundry.models.install_config import InstallConfig
from shellfoundry.utilities.installer import ShellInstaller


class TestShellInstaller(fake_filesystem_unittest.TestCase):
    def setUp(self):
        self.setUpPyfakefs()

    @patch("qpm.packaging.quali_api_client.QualiAPIClient.upload_environment_zip_file")
    @patch("qpm.packaging.quali_api_client.QualiAPIClient.__init__")
    def test_when_install_called_it_uploads_package_to_cloudshell(self, mock_quali_api_client, mock_upload_environment_zip_file):
        # Arrange
        # Constructor should return None
        mock_quali_api_client.return_value = None

        file = self.fs.CreateFile("work/dest/nut_shell.zip")

        os.chdir("work")

        install_config = InstallConfig("localhost", 9000, "YOUR_USERNAME", "YOUR_PASSWORD", "Global", "author",
                                       "online_mode", "template_location")

        shell_installer = ShellInstaller()

        # Act
        with patch("click.echo"):
            shell_installer.install("nut_shell", install_config)

        shell_full_path = "{sep}work{sep}dist{sep}nut_shell.zip".format(sep=self.fs.path_separator)
        # self.fs.path_separator + "work" + self.fs.path_separator + "dist" + self.fs.path_separator + "nut_shell.zip"

        # Assert
        mock_upload_environment_zip_file.assert_called_once_with(shell_full_path)
