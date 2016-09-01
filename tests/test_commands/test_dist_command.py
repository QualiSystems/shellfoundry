from mock import Mock
from pyfakefs import fake_filesystem_unittest

from shellfoundry.commands.dist_command import DistCommandExecutor
from tests.asserts import *


class TestDistCommandExecutor(fake_filesystem_unittest.TestCase):
    def setUp(self):
        self.setUpPyfakefs()

    def test_dependencies_downloaded(self):
        # Arrange
        self.fs.CreateFile('nut_shell/shell.yml', contents="""
shell:
    name: nut_shell
    author: Chuck Norris
    email: chuck@hollywood.io
    description: Save the world
    version: 1.0.0
    """)

        os.chdir('nut_shell')

        dependencies_packager = Mock()
        command_executor = DistCommandExecutor(dependencies_packager)

        # Act
        command_executor.dist()

        # Assert
        self.assertTrue(dependencies_packager.save_offline_dependencies.called)
        args = dependencies_packager.save_offline_dependencies.call_args[0]
        self.assertEqual(args[0].split(os.path.sep)[-1], 'requirements.txt')
        self.assertEqual(args[0].split(os.path.sep)[-2], 'src')
        self.assertEqual(args[1].split(os.path.sep)[-1], 'offline_requirements')
        self.assertEqual(args[1].split(os.path.sep)[-2], 'dist')
