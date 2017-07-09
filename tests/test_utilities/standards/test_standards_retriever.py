from pyfakefs import fake_filesystem_unittest
from mock import patch, MagicMock

from shellfoundry.utilities.standards import Standards
from cloudshell.rest.api import FeatureUnavailable


class TestStandards(fake_filesystem_unittest.TestCase):
    def setUp(self):
        self.setUpPyfakefs()

    def test_fetch_from_cloudshell(self):
        # Arrange
        cs_client = MagicMock()

        # Act
        with patch('shellfoundry.utilities.standards.standards_retriever.create_cloudshell_client',
                   return_value=cs_client):
            Standards().fetch()

        # Assert
        cs_client.get_installed_standards.assert_any_call()

    def test_fetch_from_cloudshell_failed_get_installed_standards_raises_error(self):
        # Arrange
        cs_client = MagicMock()
        cs_client.get_installed_standards.side_effect = FeatureUnavailable()

        # Act
        with patch('shellfoundry.utilities.standards.standards_retriever.create_cloudshell_client',
                   return_value=cs_client):
            with self.assertRaises(FeatureUnavailable):
                Standards().fetch()

        # Assert
        cs_client.get_installed_standards.assert_any_call()

    def test_fetch_from_local_data_folder(self):
        # Arrange
        from shellfoundry import ALTERNATIVE_STANDARDS_PATH
        self.fs.add_real_file(ALTERNATIVE_STANDARDS_PATH)

        # Act
        results = Standards().fetch(alternative=ALTERNATIVE_STANDARDS_PATH)

        standards = [{"StandardName": "cloudshell_compute_standard", "Versions": ['2.0.0']},
                     {"StandardName": "cloudshell_deployed_app_standard", "Versions": ['1.0.0']},
                     {"StandardName": "cloudshell_firewall_standard", "Versions": ['3.0.0']},
                     {"StandardName": "cloudshell_networking_standard", "Versions": ['5.0.0']},
                     {"StandardName": "cloudshell_on_prem_app_standard", "Versions": ['1.0.0']},
                     {"StandardName": "cloudshell_pdu_standard", "Versions": ['2.0.0']},
                     {"StandardName": "cloudshell_resource_standard", "Versions": ['2.0.0']}]

        # Assert
        self.assertEqual(results, standards)
