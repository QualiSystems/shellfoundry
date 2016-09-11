import os
from mock import MagicMock
from pyfakefs import fake_filesystem_unittest
from shellfoundry.commands.generate_command import GenerateCommandExecutor
from shellfoundry.models.install_config import InstallConfig


class TestGenerateCommandExecutor(fake_filesystem_unittest.TestCase):
    def setUp(self):
        self.setUpPyfakefs()

    def test_when_config_files_exist_generate_succeeds(self):
        # Arrange
        self.fs.CreateFile('nut_shell/shell.yml', contents="""
shell:
    name: nut_shell
    driver: NutShellDriver
    """)
        self.fs.CreateFile('nut_shell/cloudshell_config.yml', contents="""
install:
    host: localhost
    port: 9000
    username: YOUR_USERNAME
    password: YOUR_PASSWORD
    domain: Global
    """)
        os.chdir('nut_shell')

        driver_generator = MagicMock()

        command_executor = GenerateCommandExecutor(driver_generator=driver_generator)

        # Act
        command_executor.generate()

        # Assert
        # driver_generator.generate_driver.called
        # ('nut_shell', InstallConfig('localhost', 9000, 'YOUR_USERNAME',
        #                                                                      'YOUR_PASSWORD', 'Global'))
