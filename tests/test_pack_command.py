from asserts import *
from pyfakefs import fake_filesystem_unittest
from shellfoundry.pack_command import PackCommandExecutor


class TestMainCli(fake_filesystem_unittest.TestCase):
    def setUp(self):
        self.setUpPyfakefs()

    def test_build_package_package_created(self):
        self.fs.CreateFile('/nut_shell/shell.yml', contents="""
shell:
    name: nut_shell
""")

        self.fs.CreateFile('nut_shell/datamodel/datamodel.xml')
        self.fs.CreateFile('nut_shell/datamodel/shellconfig.xml',)
        os.chdir('nut_shell')

        # Arrange
        command_executor = PackCommandExecutor()

        # Act
        command_executor.pack()

        # Assert
        assertFileExists(self, '/nut_shell/nut_shell.zip')


