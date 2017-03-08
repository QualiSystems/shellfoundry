from mock import patch, Mock
from pyfakefs import fake_filesystem_unittest
from shellfoundry.utilities.config.config_record import ConfigRecord
from shellfoundry.utilities.config.config_context import ConfigContext
from shellfoundry.utilities.config.config_file_creation import ConfigFileCreation


class TestConfigRecord(fake_filesystem_unittest.TestCase):
    def setUp(self):
        self.setUpPyfakefs()

    @patch("shellfoundry.utilities.config.config_file_creation.open",
           create=True)  # create=True to overcome the issue with builtin methods default fallback
    @patch("shellfoundry.utilities.config.config_file_creation.click.echo")
    def test_failed_to_create_config_file(self, echo_mock, open_mock):
        # Arrange
        cfg_path = '/quali/shellfoundry/global_config.yml'
        open_mock.side_effect = [IOError('Failed to create the file, maybe it is already exists')]

        # Act
        cfg_creation = ConfigFileCreation()

        # Assert
        self.assertRaises(IOError, cfg_creation.create, cfg_path)
        echo_mock.assert_any_call('Failed to create the file, maybe it is already exists')
        echo_mock.assert_any_call('Failed to create config file')

    @patch("shellfoundry.utilities.config.config_file_creation.open", create=True)
    @patch("shellfoundry.utilities.config.config_file_creation.click.echo")
    def test_failed_to_crate_config_file_due_to_already_exists_no_error_is_raised(self, echo_mock, open_mock):
        # Arrange
        cfg_path = '/quali/shellfoundry/global_config.yml'
        open_mock.side_effect = [IOError('Failed to create the file, maybe it is already exists')]

        # Act
        with patch("shellfoundry.utilities.config.config_file_creation.os.path.exists") as path_mock:
            path_mock.side_effect = [False, True, True]
            ConfigFileCreation().create(cfg_path)

        # Assert
        echo_mock.assert_called_once_with('Creating config file...')

    @patch("shellfoundry.utilities.config.config_file_creation.click.echo")
    def test_failed_to_create_folder_hierarchy(self, echo_mock):
        # Arrange
        cfg_path = '/quali/shellfoundry/global_config.yml'

        # Act
        with patch("shellfoundry.utilities.config.config_file_creation.os.makedirs") as makedirs_mock:
            makedirs_mock.side_effect = [OSError('Failed to create the folders hierarchy')]
            self.assertRaises(OSError, ConfigFileCreation().create, cfg_path)

        # Assert
        echo_mock.assert_any_call('Failed to create config file')

    @patch("shellfoundry.utilities.config.config_file_creation.click.echo")
    def test_failed_to_save_new_record(self, echo_mock):
        # Arrange
        self.fs.CreateFile('/quali/shellfoundry/global_config.yml', contents="""
install:
  host: someaddress""")

        # Act
        with patch('shellfoundry.utilities.config.config_context.yaml') as yaml_mock:
            yaml_mock.load.side_effect = [Exception()]
            context = ConfigContext('/quali/shellfoundry/global_config.yml')
            record = ConfigRecord('key', 'value')
            record.save(context)

        # Assert
        echo_mock.assert_called_once_with('Failed to save key value')
        file_content = self.fs.GetObject('/quali/shellfoundry/global_config.yml').contents
        import os
        self.assertTrue(file_content == """
install:
  host: someaddress""", 'Expected: {}{}Actual: {}'
                        .format("""
install:
  host: someaddress""", os.linesep, file_content))

    @patch("shellfoundry.utilities.config.config_file_creation.click.echo")
    def test_failed_to_delete_record(self, echo_mock):
        # Arrange
        self.fs.CreateFile('/quali/shellfoundry/global_config.yml', contents="""
install:
  host: someaddress""")

        # Act
        with patch('shellfoundry.utilities.config.config_context.yaml') as yaml_mock:
            yaml_mock.load.side_effect = [Exception()]
            context = ConfigContext('/quali/shellfoundry/global_config.yml')
            record = ConfigRecord('host')
            record.delete(context)

        # Assert
        echo_mock.assert_called_once_with('Failed to delete key')
        file_content = self.fs.GetObject('/quali/shellfoundry/global_config.yml').contents
        import os
        self.assertTrue(file_content == """
install:
  host: someaddress""", 'Expected: {}{}Actual: {}'
                        .format("""
install:
  """, os.linesep, file_content))
