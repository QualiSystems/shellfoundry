from __future__ import annotations

import unittest
from unittest.mock import MagicMock, patch

from shellfoundry.exceptions import PlatformNameIsEmptyException
from shellfoundry.utilities.modifiers.configuration.password_modification import (
    PasswordModification,
)


class TestPasswordModification(unittest.TestCase):
    @patch("platform.node", MagicMock(return_value=""))
    def test_platform_node_returns_empty_error_is_raise(self):
        pass_mod = PasswordModification()
        with self.assertRaises(PlatformNameIsEmptyException):
            pass_mod.modify("some_value")
