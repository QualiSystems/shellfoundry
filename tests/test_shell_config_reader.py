import os
from pyfakefs import fake_filesystem_unittest
from shellfoundry.shell_config_reader import ShellConfigReader


class TestShellConfigReader(fake_filesystem_unittest.TestCase):
    def setUp(self):
        self.setUpPyfakefs()

    def test_read_config_all_settings_are_set(self):
        # Arrange
        self.fs.CreateFile('shell_name/shell.yml', contents="""
shell:
    name: nut_shell
    author: Chuck Norris
    email: chuck@hollywood.io
    description: Save the world
    version: 1.0.0
    """)
        os.chdir('shell_name')
        reader = ShellConfigReader()

        # Act
        config = reader.read()

        # Assert
        self.assertEqual(config.name, 'nut_shell')
        self.assertEqual(config.author, 'Chuck Norris')
        self.assertEqual(config.email, 'chuck@hollywood.io')
        self.assertEqual(config.description, 'Save the world')
        self.assertEqual(config.version, '1.0.0')
