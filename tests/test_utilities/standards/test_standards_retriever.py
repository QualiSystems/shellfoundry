from __future__ import annotations

from unittest.mock import MagicMock, patch

from cloudshell.rest.api import FeatureUnavailable
from pyfakefs import fake_filesystem_unittest

from shellfoundry.exceptions import StandardVersionException
from shellfoundry.utilities.standards.standards_retriever import Standards


class TestStandards(fake_filesystem_unittest.TestCase):
    def setUp(self):
        self.setUpPyfakefs()

    def test_fetch_from_cloudshell(self):
        # Arrange
        cs_client = MagicMock()
        cs_client.get_installed_standards = MagicMock(
            return_value=[
                {
                    "StandardName": "cloudshell_networking_standard",
                    "Versions": ["5.0.0", "5.0.1", "5.0.2", "5.0.3", "5.0.4"],
                },
                {
                    "StandardName": "cloudshell_resource_standard",
                    "Versions": ["2.0.0", "2.0.1", "2.0.2", "2.0.3"],
                },
                {
                    "StandardName": "cloudshell_firewall_standard",
                    "Versions": ["3.0.0", "3.0.1", "3.0.2"],
                },
            ]
        )

        expected_standards = {
            "firewall": ["3.0.0", "3.0.1", "3.0.2"],
            "networking": ["5.0.0", "5.0.1", "5.0.2", "5.0.3", "5.0.4"],
            "resource": ["2.0.0", "2.0.1", "2.0.2", "2.0.3"],
        }

        # Act
        with patch(
            "shellfoundry.utilities.standards.standards_retriever.create_cloudshell_client",  # noqa: E501
            return_value=cs_client,
        ):
            results = Standards().fetch()

        # Assert
        cs_client.get_installed_standards.assert_any_call()
        self.assertEqual(results, expected_standards)

    def test_fetch_from_local_data_folder(self):
        # Arrange
        from shellfoundry.constants import ALTERNATIVE_STANDARDS_PATH

        self.fs.add_real_file(ALTERNATIVE_STANDARDS_PATH)
        expected_standards = {
            "admin-only-custom-service": ["1.0.0"],
            "broadband-media": ["1.0.0", "1.0.1", "1.0.2", "1.0.3"],
            "cisco-aci": ["1.0.0"],
            "cloud-provider": ["1.0.0", "1.0.1"],
            "cloud-service": ["1.0.0"],
            "compute": ["2.0.0", "2.0.1"],
            "custom-service": ["1.0.0"],
            "deployed-app": ["1.0.0", "1.0.1", "1.0.2", "1.0.3"],
            "firewall": ["3.0.0", "3.0.1", "3.0.2"],
            "generic-connectable-resource": ["1.0.0"],
            "generic-resource-with-connected-commands": ["1.0.0"],
            "loadbalancer": ["1.0.0"],
            "networking": ["5.0.0", "5.0.1", "5.0.2", "5.0.3", "5.0.4"],
            "pdu": ["2.0.0", "2.0.1"],
            "resource": ["2.0.0", "2.0.1", "2.0.2", "2.0.3"],
            "sdn-controller": ["1.0.0", "1.0.1"],
            "software-asset": ["1.0.0"],
            "traffic-generator-chassis": ["1.0.0", "1.0.2", "1.0.3", "1.0.5"],
            "traffic-generator-controller": ["1.0.0", "2.0.0"],
            "virtual-traffic-generator": ["1.0.0"],
        }

        # Act
        results = Standards().fetch()

        # Assert
        self.assertEqual(results, expected_standards)

    def test_fetch_standards_failed_either_server_or_locally(self):
        # Arrange
        cs_client = MagicMock()
        cs_client.get_installed_standards.side_effect = FeatureUnavailable()

        # Act
        with patch(
            "shellfoundry.utilities.standards.standards_retriever.create_cloudshell_client",  # noqa: E501
            return_value=cs_client,
        ):
            with self.assertRaises(StandardVersionException) as context:
                Standards().fetch()  # Fetch should raise the StandardVersionException

            self.assertEqual(
                "Error during getting standards either from the server or locally",
                str(context.exception),
            )
