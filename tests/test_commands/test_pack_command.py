from pyfakefs import fake_filesystem_unittest
from tests.asserts import *
from shellfoundry.commands.pack_command import PackCommandExecutor


class TestPackCommandExecutor(fake_filesystem_unittest.TestCase):
    def setUp(self):
        self.setUpPyfakefs()

    def test_build_package_package_created(self):
        # Arrange
        self.fs.CreateFile('\\nut_shell\\shell.yml', contents="""
shell:
    name: nut_shell
    author: Chuck Norris
    email: chuck@hollywood.io
    description: Save the world
    version: 1.0.0
    """)
        self.fs.CreateFile('\\nut_shell\\datamodel\\datamodel.xml')
        self.fs.CreateFile('\\nut_shell\\datamodel\\shellconfig.xml')
        self.fs.CreateFile('\\nut_shell\\src\\driver.py')
        os.chdir('nut_shell')

        command_executor = PackCommandExecutor()

        # Act
        command_executor.pack()

        # Assert
        assertFileExists(self, '\\nut_shell\\dist\\nut_shell.zip')





