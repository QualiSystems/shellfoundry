from mock import patch
from pyfakefs import fake_filesystem_unittest
from tests.asserts import *
from shellfoundry.commands.pack_command import PackCommandExecutor


class TestPackCommandExecutor(fake_filesystem_unittest.TestCase):
    def setUp(self):
        self.setUpPyfakefs()

    @patch('click.echo')
    def test_build_package_package_created(self, echo_mock):
        # Arrange
        self.fs.CreateFile('nut_shell/shell.yml', contents="""
shell:
    name: nut_shell
    author: Chuck Norris
    email: chuck@hollywood.io
    description: Save the world
    version: 1.0.0
    """)
        self.fs.CreateFile('nut_shell/datamodel/datamodel.xml')
        self.fs.CreateFile('nut_shell/datamodel/shellconfig.xml')
        self.fs.CreateFile('nut_shell/src/driver.py')
        os.chdir('nut_shell')

        command_executor = PackCommandExecutor()

        # Act
        command_executor.pack()

        # Assert
        assertFileExists(self, 'dist/nut_shell.zip')
        echo_mock.assert_any_call(u'Shell package was successfully created:')

    @patch('click.echo')
    def test_proper_error_message_displayed_when_shell_yml_is_in_wrong_format(self, echo_mock):
        # Arrange
        self.fs.CreateFile('nut_shell/shell.yml', contents='WRONG YAML FORMAT')
        os.chdir('nut_shell')

        command_executor = PackCommandExecutor()

        # Act
        command_executor.pack()

        # Assert
        echo_mock.assert_any_call(u'shell.yml format is wrong')

    @patch('click.echo')
    def test_proper_error_message_displayed_when_shell_yml_missing(self, echo_mock):
        # Arrange
        self.fs.CreateFile('nut_shell/datamodel/datamodel.xml')
        os.chdir('nut_shell')

        command_executor = PackCommandExecutor()

        # Act
        command_executor.pack()

        # Assert
        echo_mock.assert_any_call(u'shell.yml file is missing')
