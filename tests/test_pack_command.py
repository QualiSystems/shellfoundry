import unittest
import zipfile
from asserts import *
from pyfakefs import fake_filesystem_unittest
from shellfoundry.pack_command import PackCommandExecutor


class TestPackCommandExecutor(fake_filesystem_unittest.TestCase):
    def setUp(self):
        self.setUpPyfakefs()

    @unittest.skip('make_archive does not support fakefs')
    def test_build_package_package_created(self):
        self.fs.CreateFile('nut_shell/shell.yml', contents="""
shell:
    name: nut_shell
""")

        self.fs.CreateFile('nut_shell/datamodel/datamodel.xml')
        self.fs.CreateFile('nut_shell/datamodel/shellconfig.xml')
        self.fs.CreateFile('nut_shell/src/driver.py')
        os.chdir('nut_shell')

        # Arrange
        command_executor = PackCommandExecutor()

        # Act
        command_executor.pack()

        # Assert
        assertFileExists(self, '/nut_shell/nut_shell.zip')
        with zipfile.ZipFile('/nut_shell/nut_shell.zip') as zip_file:
            zip_file.extractall('/nut_shell')
        assertFileExists(self, '/nut_shell/resource Drivers - Python/nut_shell Driver.zip')
        assertFileExists(self, '/nut_shell/Configuration/shellconfig.xml')


class TestRealPackCommandExecutor(unittest.TestCase):
    @unittest.skip('integration test')
    def test__(self):
        os.chdir('c:\\work\\github\\shellfoundry\\net_shell')
        command_executor = PackCommandExecutor()

        # Act
        command_executor.pack()





