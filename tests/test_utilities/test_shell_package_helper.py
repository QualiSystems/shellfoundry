import unittest

from shellfoundry.utilities.shell_package_helper import ShellPackageHelper


class TestShellPackageHelper(unittest.TestCase):
    def test_get_shell_name_should_be_capitalized(self):
        shell_name = ShellPackageHelper.get_shell_name('work/folders/nut-shell')

        self.assertEqual(shell_name, 'NutShell')
