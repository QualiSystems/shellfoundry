import os

from pyfakefs import fake_filesystem_unittest
from shellfoundry.config_reader import ConfigReader


class TestConfigReader(fake_filesystem_unittest.TestCase):
    def setUp(self):
        self.setUpPyfakefs()

    def test_read_config_all_settings_are_set(self):
        # Arrange

        self.fs.CreateFile('shell_name/shellfoundry.yml', contents="""
install:
    host: my_server
    port: 123
    username: my_user
    password: my_password
    domain: my_domain
    """)
        os.chdir("shell_name")
        reader = ConfigReader()

        # Act
        project = reader.read('shellfoundry.yml')

        # Assert
        self.assertEqual(project.name, 'shell_name')
        self.assertEqual(project.install.host, 'my_server')
        self.assertEqual(project.install.port, 123)
        self.assertEqual(project.install.username, 'my_user')
        self.assertEqual(project.install.password, 'my_password')
        self.assertEqual(project.install.domain, 'my_domain')

    def test_read_only_install_section_default_settings(self):
        # Arrange
        self.fs.CreateFile('shellfoundry.yml', contents='install:')
        reader = ConfigReader()

        # Act
        project = reader.read('shellfoundry.yml')

        # Assert
        self.assertEqual(project.install.host, 'localhost')
        self.assertEqual(project.install.port, 9000)
        self.assertEqual(project.install.username, 'admin')
        self.assertEqual(project.install.password, 'admin')
        self.assertEqual(project.install.domain, 'Global')

    def test_read_file_does_not_exist_default_settings(self):
        # Arrange
        reader = ConfigReader()

        # Act
        project = reader.read('shellfoundry.yml')

        # Assert
        self.assertEqual(project.install.host, 'localhost')
        self.assertEqual(project.install.port, 9000)
        self.assertEqual(project.install.username, 'admin')
        self.assertEqual(project.install.password, 'admin')
        self.assertEqual(project.install.domain, 'Global')

    def test_read_file_is_empty_default_settings(self):
        # Arrange
        self.fs.CreateFile('shellfoundry.yml', contents='')
        reader = ConfigReader()

        # Act
        project = reader.read('shellfoundry.yml')

        # Assert
        self.assertEqual(project.install.host, 'localhost')
        self.assertEqual(project.install.port, 9000)
        self.assertEqual(project.install.username, 'admin')
        self.assertEqual(project.install.password, 'admin')
        self.assertEqual(project.install.domain, 'Global')
