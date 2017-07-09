import unittest

from mock import patch, Mock
from shellfoundry.utilities import is_index_version_greater_than_current

patch.object = patch.object


class TestVersionsHelpers(unittest.TestCase):
    def test_current_version_greater_than_index(self):
        # Arrange
        releases = {'0.2.7': 'data',
                    '0.2.8': 'some other data',
                    '1.0.0': 'amazing data'}

        server_proxy = Mock(package_releases=Mock(return_value=releases))

        # Act
        with patch('shellfoundry.utilities.get_installed_version', return_value='1.0.0'), \
             patch('shellfoundry.utilities.ServerProxy', return_value=server_proxy):
            is_greater_version, is_major_release = is_index_version_greater_than_current()

        # Assert
        self.assertFalse(is_greater_version)
        self.assertFalse(is_major_release)

    def test_current_version_lower_than_index_by_a_patch(self):
        # Arrange
        releases = {'0.2.7': 'data',
                    '0.2.8': 'some other data'}

        server_proxy = Mock(package_releases=Mock(return_value=releases))

        # Act
        with patch('shellfoundry.utilities.get_installed_version', return_value='0.2.7'), \
             patch('shellfoundry.utilities.ServerProxy', return_value=server_proxy):
            is_greater_version, is_major_release = is_index_version_greater_than_current()

        # Assert
        self.assertTrue(is_greater_version)
        self.assertFalse(is_major_release)

    def test_current_version_lower_than_index_by_a_major(self):
        # Arrange
        releases = {'0.2.7': 'data',
                    '0.2.8': 'some other data',
                    '1.0.0': 'amazing data'}

        server_proxy = Mock(package_releases=Mock(return_value=releases))

        # Act
        with patch('shellfoundry.utilities.get_installed_version', return_value='0.2.7'), \
             patch('shellfoundry.utilities.ServerProxy', return_value=server_proxy):
            is_greater_version, is_major_release = is_index_version_greater_than_current()

        # Assert
        self.assertTrue(is_greater_version)
        self.assertTrue(is_major_release)

    def test_current_version_is_equal_to_index_version(self):
        # Arrange
        releases = {'0.2.7': 'data'}

        server_proxy = Mock(package_releases=Mock(return_value=releases))

        # Act
        with patch('shellfoundry.utilities.get_installed_version', return_value='0.2.7'), \
             patch('shellfoundry.utilities.ServerProxy', return_value=server_proxy):
            is_greater_version, is_major_release = is_index_version_greater_than_current()

        # Assert
        self.assertFalse(is_greater_version)
        self.assertFalse(is_major_release)
