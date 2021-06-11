#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import unittest

if sys.version_info >= (3, 0):
    from unittest.mock import MagicMock, patch
else:
    from mock import MagicMock, patch

from shellfoundry.models.install_config import InstallConfig


class TestInstallConfig(unittest.TestCase):
    def test_two_instances_should_be_equal(self):
        config1 = InstallConfig(
            host="localhost",
            port=9000,
            username="username",
            password="password",
            domain="Global",
            author="Quali",
            online_mode="Online_mode",
            template_location="template_location",
            github_login="github_login",
            github_password="password",
        )
        config2 = InstallConfig(
            host="localhost",
            port=9000,
            username="username",
            password="password",
            domain="Global",
            author="Quali",
            online_mode="Online_mode",
            template_location="template_location",
            github_login="github_login",
            github_password="password",
        )

        self.assertEqual(config1, config2)

    def test_two_instances_should_not_be_equal(self):
        config1 = InstallConfig(
            "localhost",
            9000,
            "YOUR_USERNAME",
            "YOUR_PASSWORD",
            "Global",
            "author",
            "online_mode",
            "template_location",
            "github_login",
            "github_password",
        )
        config2 = InstallConfig(
            "remote",
            1,
            "U",
            "P",
            "Local",
            "co-author",
            "False",
            "local_templates_location",
            "github_login_new",
            "github_password_new",
        )

        self.assertNotEqual(config1, config2)

    @patch("platform.node", MagicMock(return_value="machine-name-here"))
    def test_non_encrypted_password_field_stays_regular(self):
        config = InstallConfig(
            "localhost",
            9000,
            "YOUR_USERNAME",
            "admin",
            "Global",
            "author",
            "online_mode",
            "template_location",
            "github_login",
            "github_password",
        )
        self.assertEqual("admin", config.password)

    @patch("platform.node", MagicMock(return_value="machine-name-here"))
    def test_non_encrypted_github_password_field_stays_regular(self):
        config = InstallConfig(
            "localhost",
            9000,
            "YOUR_USERNAME",
            "admin",
            "Global",
            "author",
            "online_mode",
            "template_location",
            "github_login",
            "admin",
        )
        self.assertEqual("admin", config.github_password)
