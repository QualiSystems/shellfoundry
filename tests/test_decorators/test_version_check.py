#!/usr/bin/python

import unittest
from io import StringIO
from unittest.mock import patch

from click import Abort

from shellfoundry.decorators import shellfoundry_version_check


@shellfoundry_version_check(abort_if_major=False)
def do_not_abort():
    print("vido", end="")  # noqa: T001


@shellfoundry_version_check(abort_if_major=True)
def abort_if_major():
    print("vido", end="")  # noqa: T001


class TestShellFoundryVersionCheck(unittest.TestCase):
    @patch("sys.stdout", new_callable=StringIO)
    def test_version_check_when_current_is_greater_than_index(self, stdout_mock):
        # Act
        with patch(
            "shellfoundry.utilities.get_installed_version", return_value="5.0.0"
        ), patch("shellfoundry.utilities.max_version_from_index", return_value="0.2.9"):
            do_not_abort()

        # Assert
        self.assertEqual(stdout_mock.getvalue(), "vido")

    @patch("sys.stdout", new_callable=StringIO)
    def test_version_check_when_current_is_lower_than_index_but_not_major_version(
        self, stdout_mock
    ):
        # Act
        with patch(
            "shellfoundry.utilities.get_installed_version", return_value="0.2.7"
        ), patch("shellfoundry.utilities.max_version_from_index", return_value="0.3.0"):
            do_not_abort()

        # Assert
        self.assertEqual(
            stdout_mock.getvalue(),
            "vido\nThere is a new version of shellfoundry available, please upgrade by running: pip install shellfoundry --upgrade\n",  # noqa: E501
        )

    @patch("sys.stdout", new_callable=StringIO)
    def test_version_check_when_current_is_lower_than_index_and_its_major_version(
        self, stdout_mock
    ):
        # Act
        with patch(
            "shellfoundry.utilities.get_installed_version", return_value="0.2.7"
        ), patch("shellfoundry.utilities.max_version_from_index", return_value="1.0.0"):
            do_not_abort()

        # Assert
        self.assertEqual(
            stdout_mock.getvalue(),
            "vido\nThis version of shellfoundry is not supported anymore, please upgrade by running: pip install shellfoundry --upgrade\n",  # noqa: E501
        )

    @patch("sys.stdout", new_callable=StringIO)
    def test_version_check_when_current_is_equal_to_index(self, stdout_mock):
        # Act
        with patch(
            "shellfoundry.utilities.get_installed_version", return_value="1.0.0"
        ), patch("shellfoundry.utilities.max_version_from_index", return_value="1.0.0"):
            do_not_abort()

        # Assert
        self.assertEqual(stdout_mock.getvalue(), "vido")

    @patch("sys.stdout", new_callable=StringIO)
    def test_version_check_when_current_is_lower_than_index_and_its_major_version_validate_abort(  # noqa: E501
        self, stdout_mock
    ):
        # Act
        with patch(
            "shellfoundry.utilities.get_installed_version", return_value="0.2.7"
        ), patch("shellfoundry.utilities.max_version_from_index", return_value="1.0.0"):
            self.assertRaises(Abort, abort_if_major)

        # Assert
        self.assertEqual(
            stdout_mock.getvalue(),
            "This version of shellfoundry is not supported anymore, please upgrade by running: pip install shellfoundry --upgrade\n\n",  # noqa: E501
        )
