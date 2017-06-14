import unittest

from mock import patch, Mock
from shellfoundry.utilities.standards import StandardVersions


class TestStandardsVersions(unittest.TestCase):
    def test_get_latest_version_returns_the_greater_version(self):
        # Arrange
        standards = [{'StandardName': "cloudshell_networking_standard", 'Versions': ['2.0.0', '2.0.1']}]

        # Act
        result = StandardVersions(standards).get_latest_version('networking')

        # Assert
        self.assertTrue(result == '2.0.1', 'actual result: ' + result)

    def _est_get_latest_version_when_only_one_is_available(self):
        # Arrange
        standards = [{'StandardName': "cloudshell_networking_standard", 'Versions': ['2.0.0']}]

        # Act
        result = StandardVersions(standards).get_latest_version('networking')

        # Assert
        self.assertTrue(result == '2.0.0', 'actual result: ' + result)

    def test_get_latest_version_failed_to_find_requested_standard(self):
        # Arrange
        standards = [{'StandardName': "cloudshell_networking_standard", 'Versions': ['2.0.0']}]

        # Act
        with self.assertRaises(Exception) as context:
            StandardVersions(standards).get_latest_version('resource')

        # Assert
        self.assertTrue(str(context.exception) == 'Failed to find latest version',
                        "Actual: {}".format(context.exception))

    def test_get_latest_version_find_requested_standard_within_lots_of_standards(self):
        # Arrange
        standards = [{'StandardName': "cloudshell_networking_standard", 'Versions': ['2.0.0']},
                     {'StandardName': "cloudshell_resource_standard", 'Versions': ['5.0.0', '5.0.1']},
                     {'StandardName': "cloudshell_vido_standard", 'Versions': ['3.0.1', '3.0.2', '3.0.3']}]

        # Act
        result = StandardVersions(standards).get_latest_version('resource')

        # Assert
        self.assertTrue(result == '5.0.1', 'actual result: ' + result)

    def test_standards_list_empty_raises_an_exception(self):
        # Arrange
        standards = []

        # Act
        with patch('os.path.join', new=Mock(return_value='/shellfoundry/folder/data/standards.json')),\
             patch('os.path.dirname', new=Mock(return_value='/shellfoundry/folder')):
            with self.assertRaises(Exception) as context:
                StandardVersions(standards).get_latest_version('resource')

        # Assert
        self.assertTrue(
            str(context.exception) == 'Standards list is empty. Please verify that {} exists'.format(
                '/shellfoundry/folder/data/standards.json'), "Actual: {}".format(context.exception))
