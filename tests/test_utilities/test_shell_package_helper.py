import unittest

from shellfoundry.utilities.shell_package import ShellPackage


class TestShellPackageHelper(unittest.TestCase):
    def test_get_shell_name_should_be_capitalized(self):
        # Arrange
        shell_package = ShellPackage('work/folders/nut-shell')

        # Act
        shell_name = shell_package.get_shell_name()

        # Assert
        self.assertEqual(shell_name, 'NutShell')
