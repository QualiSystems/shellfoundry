#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys

if sys.version_info >= (3, 0):
    from unittest.mock import patch
else:
    from mock import patch
from pyfakefs import fake_filesystem_unittest

from shellfoundry.models.install_config import InstallConfig
from shellfoundry.utilities.installer import ShellInstaller


class TestShellInstaller(fake_filesystem_unittest.TestCase):
    def setUp(self):
        self.setUpPyfakefs()

    @patch("cloudshell.rest.api.PackagingRestApiClient.import_package")
    @patch("cloudshell.rest.api.PackagingRestApiClient.__init__")
    def test_when_install_called_it_uploads_package_to_cloudshell(
        self, mock_quali_api_client, mock_import_package
    ):
        # Arrange
        # Constructor should return None
        mock_quali_api_client.return_value = None

        self.fs.create_file("work/dest/nut_shell.zip")

        os.chdir("work")

        install_config = InstallConfig(
            "localhost",
            9000,
            "YOUR_USERNAME",
            "LAUOKwE=",
            "Global",
            "author",
            "online_mode",
            "template_location",
            "github_login",
            "LAUOKwE=",
        )

        shell_installer = ShellInstaller()

        # Act
        with patch("click.echo"):
            shell_installer.install("nut_shell", install_config)

        shell_full_path = "{sep}work{sep}dist{sep}nut_shell.zip".format(
            sep=self.fs.path_separator
        )

        # Assert
        mock_import_package.assert_called_once_with(shell_full_path)
