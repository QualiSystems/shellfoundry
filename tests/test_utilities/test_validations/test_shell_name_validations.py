import unittest

from shellfoundry.utilities.validations import ShellNameValidations


class TestShellNameValidations(unittest.TestCase):
    def test_shell_name_correct_name_used_success(self):
        # Arrange
        shell_name = 'vido'
        validations = ShellNameValidations()

        # Act
        result = validations.validate_shell_name(shell_name)

        # Assert
        self.assertTrue(result)

    def test_shell_name_with_dash_used_success(self):
        # Arrange
        shell_name = 'vido-king'
        validations = ShellNameValidations()

        # Act
        result = validations.validate_shell_name(shell_name)

        # Assert
        self.assertTrue(result)

    def test_shell_name_starts_with_a_number_validation_failed(self):
        # Arrange
        shell_name = '15vido'
        validations = ShellNameValidations()

        # Act
        result = validations.validate_shell_name(shell_name)

        # Assert
        self.assertFalse(result)

    def test_shell_name_contains_backward_slash_validation_failed(self):
        # Arrange
        shell_name = 'vido\\bsd'
        validations = ShellNameValidations()

        # Act
        result = validations.validate_shell_name(shell_name)

        # Assert
        self.assertFalse(result)

    def test_shell_name_contains_forward_slash_validation_failed(self):
        # Arrange
        shell_name = 'vido/bsd'
        validations = ShellNameValidations()

        # Act
        result = validations.validate_shell_name(shell_name)

        # Assert
        self.assertFalse(result)

    def test_shell_name_too_long_validation_failed(self):
        # Arrange
        shell_name = 'vidoisthekingofthewholeuniverseandthatincludesofcourseallunknownworldsinthefarfarreachesoftheuniverse'
        validations = ShellNameValidations()

        # Act
        result = validations.validate_shell_name(shell_name)

        # Assert
        self.assertFalse(result)
