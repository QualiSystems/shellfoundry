#!/usr/bin/python

import os
from unittest.mock import patch

from pyfakefs import fake_filesystem_unittest

from shellfoundry.utilities.python_dependencies_packager import (
    PythonDependenciesPackager,
)


class TestPythonDependenciesPackager(fake_filesystem_unittest.TestCase):
    def setUp(self):
        self.setUpPyfakefs()

    def test_calls_pip_to_download_dependencies(self):
        requirements_file = "req/requirements.requirements_file"
        self.fs.create_file(requirements_file, contents="")

        with patch(
            "shellfoundry.utilities.python_dependencies_packager.pip_main"
        ) as mock_pip:
            # Act
            packager = PythonDependenciesPackager()
            packager.save_offline_dependencies(requirements_file, "dst")
            self.assertTrue(mock_pip.called, "pip.main should be called")
            _, call_params, _ = mock_pip.mock_calls[0]
            main_params = call_params[0]
            self.assertIn("download", main_params)
            self.assertIn(
                "--requirement=req/requirements.requirements_file", main_params
            )
            self.assertIn("--dest=dst", main_params)

    def test_calls_pip_to_download_dependencies_with_proxy(self):
        with patch(
            "shellfoundry.utilities.python_dependencies_packager.os.environ.get"
        ) as environ_mock:
            environ_mock.return_value = "HTTP PROXY"

            requirements_file = "req/requirements.requirements_file"
            self.fs.create_file(requirements_file, contents="")

            with patch(
                "shellfoundry.utilities.python_dependencies_packager.pip_main"
            ) as mock_pip:
                # Act
                packager = PythonDependenciesPackager()
                packager.save_offline_dependencies(requirements_file, "dst")
                self.assertTrue(mock_pip.called, "pip.main should be called")
                _, call_params, _ = mock_pip.mock_calls[0]
                main_params = call_params[0]
                self.assertIn("download", main_params)
                self.assertIn(
                    "--requirement=req/requirements.requirements_file", main_params
                )
                self.assertIn("--dest=dst", main_params)
                self.assertIn("--proxy", main_params)
                self.assertIn("HTTP PROXY", main_params)

    def test_removed_old_files_before_running(self):
        requirements_file = "req/requirements.requirements_file"
        self.fs.create_file(requirements_file, contents="")
        file = "dst/test.txt"
        self.fs.create_file(file, contents="")
        nested_file = "dst/nested/test.txt"
        self.fs.create_file(nested_file, contents="")

        with patch(
            "shellfoundry.utilities.python_dependencies_packager.pip_main"
        ) as mock_pip:  # noqa: F841
            # Act
            packager = PythonDependenciesPackager()
            packager.save_offline_dependencies(requirements_file, "dst")

        self.assertFalse(os.path.exists(file))
        self.assertFalse(os.path.exists(nested_file))

    def test_does_nothing_if_requirements_file_does_not_exist(self):
        requirements_file = "req/requirements.requirements_file"

        with patch(
            "shellfoundry.utilities.python_dependencies_packager.pip_main"
        ) as mock_pip:
            # Act
            packager = PythonDependenciesPackager()
            packager.save_offline_dependencies(requirements_file, "dst")
        mock_pip.main.assert_not_called()
