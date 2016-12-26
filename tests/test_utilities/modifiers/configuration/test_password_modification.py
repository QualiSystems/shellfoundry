import unittest

from mock import patch, Mock
from shellfoundry.utilities.modifiers.configuration.password_modification import  PasswordModification
from shellfoundry.exceptions import PlatformNameIsEmptyException

class TestPasswordModification(unittest.TestCase):
    @patch('platform.node', Mock(return_value=''))
    def test_platform_node_returns_empty_error_is_raise(self):
        pass_mod = PasswordModification()
        with self.assertRaises(PlatformNameIsEmptyException):
            pass_mod.modify('some_value')

