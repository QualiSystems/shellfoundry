import unittest

from mock import Mock, patch
from urllib2 import HTTPError
from shellfoundry.exceptions import FatalError
from shellfoundry.utilities.cloudshell_api import CloudShellClient, create_cloudshell_client

patch.object = patch.object


class TestClientWrapper(unittest.TestCase):
    def test_client_wrapper_raises_an_error_when_create_client_fails(self):
        # Act
        with patch.object(CloudShellClient, 'create_client', side_effect=FatalError('failure')):
            with self.assertRaises(FatalError) as context:
                create_cloudshell_client()

        # Assert
        self.assertEqual(context.exception.message, 'failure')

    @patch('shellfoundry.utilities.cloudshell_api.client_wrapper.PackagingRestApiClient')
    def test_client_wrapper_raises_an_error_when_create_client_fails_after_retries_regular_exception(self, api_mock):
        # Arrange
        api_mock.side_effect = [Exception(), Exception()]

        # Act
        with self.assertRaises(FatalError) as context:
            create_cloudshell_client(retries=2)

        # Assert
        self.assertEqual(context.exception.message, CloudShellClient.ConnectionFailureMessage)

    @patch('shellfoundry.utilities.cloudshell_api.client_wrapper.PackagingRestApiClient', new_callable=Mock())
    def test_client_wrapper_raises_an_error_when_create_client_fails_after_retries_http_error(self, api_mock):
        # Arrange
        error = HTTPError('url', 401, 'not found', None, None)
        api_mock.side_effect = [error, error]

        # Act
        with self.assertRaises(FatalError) as context:
            create_cloudshell_client(retries=2)

        # Assert
        self.assertEqual(context.exception.message, u'Login to CloudShell failed. Please verify the credentials in the config')

    @patch('shellfoundry.utilities.cloudshell_api.client_wrapper.PackagingRestApiClient')
    def test_client_wrapper_raises_an_error_when_create_client_fails_after_retries(self, api_mock):
        # Arrange
        api_mock.side_effect = [Exception(), api_mock]

        # Act
        with patch.object(CloudShellClient, 'create_client', side_effect=FatalError('failure')):
            with self.assertRaises(FatalError) as context:
                create_cloudshell_client(retries=2)

        # Assert
        self.assertEqual(context.exception.message, 'failure')

    @patch('shellfoundry.utilities.cloudshell_api.client_wrapper.PackagingRestApiClient')
    def test_client_wrapper_creates_client_successfully(self, api_mock):
        # Arrange
        api_mock.return_value = api_mock

        # Act
        cs_client = create_cloudshell_client()

        # Assert
        self.assertEqual(cs_client, api_mock)

    @patch('shellfoundry.utilities.cloudshell_api.client_wrapper.PackagingRestApiClient')
    def test_client_wrapper_creates_client_successfully_after_initial_exception(self, api_mock):
        # Arrange
        api_mock.side_effect = [Exception(), api_mock]

        # Act
        cs_client = create_cloudshell_client(retries=2)

        # Assert
        self.assertEqual(cs_client, api_mock)
