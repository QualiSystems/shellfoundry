import unittest
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
