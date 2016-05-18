import os
from pyfakefs import fake_filesystem_unittest
from shellfoundry.config_reader import CloudShellConfigReader


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
        reader = CloudShellConfigReader()

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
        reader = CloudShellConfigReader()

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
        reader = CloudShellConfigReader()

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
        reader = CloudShellConfigReader()

        # Act
        config = reader.read()

        # Assert
        self.assertEqual(config.host, 'localhost')
        self.assertEqual(config.port, 9000)
        self.assertEqual(config.username, 'admin')
        self.assertEqual(config.password, 'admin')
        self.assertEqual(config.domain, 'Global')
