import unittest

from mock import Mock, patch
from shellfoundry.models.install_config import InstallConfig


class TestInstallConfig(unittest.TestCase):
    def test_two_instances_should_be_equal(self):
        config1 = InstallConfig('localhost', 9000, 'YOUR_USERNAME', 'YOUR_PASSWORD', 'Global')
        config2 = InstallConfig('localhost', 9000, 'YOUR_USERNAME', 'YOUR_PASSWORD', 'Global')

        self.assertEqual(config1, config2)

    def test_two_instances_should_not_be_equal(self):
        config1 = InstallConfig('localhost', 9000, 'YOUR_USERNAME', 'YOUR_PASSWORD', 'Global')
        config2 = InstallConfig('remote', 1, 'U', 'P', 'Local')

        self.assertNotEqual(config1, config2)

    @patch('platform.node', Mock(return_value='machine-name-here'))
    def test_encrypted_password_field_becomes_decrypted(self):
        config = InstallConfig('localhost', 9000, 'YOUR_USERNAME', 'DAUOAQc=', 'Global')
        self.assertEqual("admin", config.password)

    @patch('platform.node', Mock(return_value='machine-name-here'))
    def test_non_encrypted_password_field_stays_regular(self):
        config = InstallConfig('localhost', 9000, 'YOUR_USERNAME', 'admin', 'Global')
        self.assertEqual("admin", config.password)

