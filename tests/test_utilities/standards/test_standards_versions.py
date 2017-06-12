import unittest

from shellfoundry.utilities.standards import StandardVersions


class TestStandardsVersions(unittest.TestCase):
    def test_get_latest_version_returns_the_greater_version(self):
        # Arrange
        standards = [{'StandardName': "cloudshell_networking_standard", 'Versions': ['2.0.0', '2.0.1']}]

        # Act
        result = StandardVersions(standards).get_latest_version('networking')

        # Assert
        self.assertTrue(result == '2.0.1', 'actual result: ' + result)

    def _test_get_latest_version_when_only_one_is_available(self):
        # Arrange
        standards = [{'StandardName': "cloudshell_networking_standard", 'Versions': ['2.0.0']}]

        # Act
        result = StandardVersions(standards).get_latest_version('networking')

        # Assert
        self.assertTrue(result == '2.0.0', 'actual result: ' + result)
