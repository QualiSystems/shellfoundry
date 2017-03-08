import os

from pyfakefs import fake_filesystem_unittest
from mock import patch
from shellfoundry.utilities.config_reader import Configuration, CloudShellConfigReader, ShellFoundryConfig


class TestConfigReader(fake_filesystem_unittest.TestCase):
    def setUp(self):
        self.setUpPyfakefs()

    def test_read_config_all_settings_are_set(self):
        # Arrange
        self.fs.CreateFile('shell_name/cloudshell_config.yml', contents="""
install:
    host: my_server
    port: 123
    username: my_user
    password: my_password
    domain: my_domain
    """)
        os.chdir('shell_name')
        reader = Configuration(CloudShellConfigReader())

        # Act
        config = reader.read()

        # Assert
        self.assertEqual(config.host, 'my_server')
        self.assertEqual(config.port, 123)
        self.assertEqual(config.username, 'my_user')
        self.assertEqual(config.password, 'my_password')
        self.assertEqual(config.domain, 'my_domain')

    def test_read_only_install_section_default_settings(self):
        # Arrange
        self.fs.CreateFile('shell_name/cloudshell_config.yml', contents='install:')
        os.chdir('shell_name')
        reader = Configuration(CloudShellConfigReader())

        # Act
        config = reader.read()

        # Assert
        self.assertEqual(config.host, 'localhost')
        self.assertEqual(config.port, 9000)
        self.assertEqual(config.username, 'admin')
        self.assertEqual(config.password, 'admin')
        self.assertEqual(config.domain, 'Global')

    def test_read_file_does_not_exist_default_settings(self):
        # Arrange
        reader = Configuration(CloudShellConfigReader())

        # Act
        config = reader.read()

        # Assert
        self.assertEqual(config.host, 'localhost')
        self.assertEqual(config.port, 9000)
        self.assertEqual(config.username, 'admin')
        self.assertEqual(config.password, 'admin')
        self.assertEqual(config.domain, 'Global')

    def test_read_file_is_empty_default_settings(self):
        # Arrange
        self.fs.CreateFile('shell_name/cloudshell_config.yml', contents='')
        os.chdir('shell_name')
        reader = Configuration(CloudShellConfigReader())

        # Act
        config = reader.read()

        # Assert
        self.assertEqual(config.host, 'localhost')
        self.assertEqual(config.port, 9000)
        self.assertEqual(config.username, 'admin')
        self.assertEqual(config.password, 'admin')
        self.assertEqual(config.domain, 'Global')

    @patch("shellfoundry.utilities.config.config_providers.click.get_app_dir")
    def test_read_config_data_from_global_configuration(self, get_app_dir_mock):
        # Arrange
        self.fs.CreateFile('Quali/shellfoundry/global_config.yml', contents="""
install:
  host: somehostaddress
""")
        get_app_dir_mock.return_value = 'Quali/shellfoundry/'
        reader = Configuration(CloudShellConfigReader())

        # Act
        config = reader.read()

        # Assert
        self.assertEqual(config.host, 'somehostaddress')
        self.assertEqual(config.port, 9000)
        self.assertEqual(config.username, 'admin')
        self.assertEqual(config.password, 'admin')
        self.assertEqual(config.domain, 'Global')

    def test_read_shellfoundry_settings_all_config_are_set(self):
        # Arrange
        self.fs.CreateFile('shell_name/cloudshell_config.yml', contents="""
install:
    defaultview: gen2
    """)
        os.chdir('shell_name')
        reader = Configuration(ShellFoundryConfig())

        # Act
        settings = reader.read()

        #Assert
        self.assertEqual(settings.defaultview, 'gen2')

    def test_read_shellfoundry_settings_not_config_file_reads_default(self):
        # Arrange
        reader = Configuration(ShellFoundryConfig())

        # Act
        settings = reader.read()

        #Assert
        self.assertEqual(settings.defaultview, 'gen2')

    def test_non_valid_config_file_read_default(self):
        self.fs.CreateFile('shell_name/cloudshell_config.yml', contents="""
invalidsection:
    defaultview: tosca
    """)
        os.chdir('shell_name')
        reader = Configuration(ShellFoundryConfig())

        # Act
        settings = reader.read()

        # Assert
        self.assertEqual(settings.defaultview, 'gen2')
