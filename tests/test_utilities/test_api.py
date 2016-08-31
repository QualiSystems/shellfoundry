from mock import patch, Mock
from pyfakefs import fake_filesystem_unittest
from requests import Response
from shellfoundry.utilities.api import CloudShellRestApiClient


class TestCloudShellRestApiClient(fake_filesystem_unittest.TestCase):
    def setUp(self):
        self.setUpPyfakefs()

    @patch('shellfoundry.utilities.api.urllib2.build_opener')
    def test_login(self, mock_build_opener):
        # Arrange
        mock_url = Mock()
        mock_url.read = Mock(return_value='TOKEN')
        mock_opener = Mock()
        mock_opener.open = Mock(return_value=mock_url)
        mock_build_opener.return_value = mock_opener

        # Act
        CloudShellRestApiClient('SERVER', 9000, 'USER', 'PASS', 'Global')

        # Assert
        self.assertTrue(mock_opener.open.called, 'open should be called')

    @patch('shellfoundry.utilities.api.urllib2.build_opener')
    @patch('shellfoundry.utilities.api.post')
    def test_add_shell(self, mock_post, mock_build_opener):
        # Arrange
        mock_url = Mock()
        mock_url.read = Mock(return_value='TOKEN')
        mock_opener = Mock()
        mock_opener.open = Mock(return_value=mock_url)
        mock_build_opener.return_value = mock_opener
        client = CloudShellRestApiClient('SERVER', 9000, 'USER', 'PASS', 'Global')
        self.fs.CreateFile('work//NutShell.zip', contents='ZIP CONTENT')
        mock_post.return_value = Response()
        mock_post.return_value.status_code = 201  # Created

        # Act
        client.add_shell('work//NutShell.zip')

        # Assert
        self.assertTrue(mock_post.called, 'Post should be called')
        self.assertEqual(mock_post.call_args[0][0], 'http://SERVER:9000/API/Shells')
        self.assertEqual(mock_post.call_args[1]['headers']['Authorization'], 'Basic TOKEN')

    @patch('shellfoundry.utilities.api.urllib2.build_opener')
    @patch('shellfoundry.utilities.api.post')
    def test_update_shell(self, mock_post, mock_build_opener):
        # Arrange
        mock_url = Mock()
        mock_url.read = Mock(return_value='TOKEN')
        mock_opener = Mock()
        mock_opener.open = Mock(return_value=mock_url)
        mock_build_opener.return_value = mock_opener
        client = CloudShellRestApiClient('SERVER', 9000, 'USER', 'PASS', 'Global')
        self.fs.CreateFile('work//NutShell.zip', contents='ZIP CONTENT')
        mock_post.return_value = Response()
        mock_post.return_value.status_code = 200  # Ok

        # Act
        client.update_shell('work//NutShell.zip')

        # Assert
        self.assertTrue(mock_post.called, 'Post should be called')
        self.assertEqual(mock_post.call_args[0][0], 'http://SERVER:9000/API/Shells/NutShell')
        self.assertEqual(mock_post.call_args[1]['headers']['Authorization'], 'Basic TOKEN')

