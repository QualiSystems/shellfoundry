#!/usr/bin/python
# -*- coding: utf-8 -*-

import unittest

from mock import Mock, patch
from shellfoundry.models.install_config import InstallConfig


class TestInstallConfig(unittest.TestCase):
    def test_two_instances_should_be_equal(self):
        config1 = InstallConfig("localhost", 9000, "YOUR_USERNAME", "YOUR_PASSWORD", "Global", "author",
                                "online_mode", "template_location")
        config2 = InstallConfig("localhost", 9000, "YOUR_USERNAME", "YOUR_PASSWORD", "Global", "author",
                                "online_mode", "template_location")

        self.assertEqual(config1, config2)

    def test_two_instances_should_not_be_equal(self):
        config1 = InstallConfig("localhost", 9000, "YOUR_USERNAME", "YOUR_PASSWORD", "Global", "author",
                                "online_mode", "template_location")
        config2 = InstallConfig("remote", 1, "U", "P", "Local", "co-author", "False", "local_templates_location")

        self.assertNotEqual(config1, config2)

    @patch("platform.node", Mock(return_value="machine-name-here"))
    def test_encrypted_password_field_becomes_decrypted(self):
        config = InstallConfig("localhost", 9000, "YOUR_USERNAME", "DAUOAQc=", "Global", "author",
                               "online_mode", "template_location")
        self.assertEqual("admin", config.password)

    @patch("platform.node", Mock(return_value="machine-name-here"))
    def test_non_encrypted_password_field_stays_regular(self):
        config = InstallConfig("localhost", 9000, "YOUR_USERNAME", "admin", "Global", "author",
                               "online_mode", "template_location")
        self.assertEqual("admin", config.password)

