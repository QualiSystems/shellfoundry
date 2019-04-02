#!/usr/bin/python
# -*- coding: utf-8 -*-

import os

from cookiecutter.main import cookiecutter
from mock import patch, MagicMock
from unittest import TestCase

from shellfoundry.utilities.cookiecutter_integration import CookiecutterTemplateCompiler


class TestCookiecutterTemplateCompiler(TestCase):
    @patch("shellfoundry.utilities.cookiecutter_integration.cookiecutter")
    def test_when_in_local_dir_mode_output_folder_is_to_same_dir(self, cookiecutter_mock):
        CookiecutterTemplateCompiler().compile_template(shell_name="shell",
                                                        template_path="template",
                                                        extra_context={},
                                                        running_on_same_folder=True)
        cookiecutter_mock.smarter_assert_called_once_with(
            cookiecutter,
            template="template",
            output_dir=os.path.pardir)

    @patch("shellfoundry.utilities.cookiecutter_integration.cookiecutter")
    def test_when_not_in_local_dir_mode_output_folder_is_to_sub_dir(self, cookiecutter_mock):
        CookiecutterTemplateCompiler().compile_template(shell_name="shell",
                                                        template_path="template",
                                                        extra_context={},
                                                        running_on_same_folder=False)
        cookiecutter_mock.smarter_assert_called_once_with(
            cookiecutter,
            template="template",
            output_dir=os.path.curdir)

    @patch("shellfoundry.utilities.cookiecutter_integration.cookiecutter")
    @patch("shellfoundry.utilities.cookiecutter_integration.Configuration")
    def test_project_name_automatically_added_to_extra_context(self, configuration_class, cookiecutter_mock):
        configuration = MagicMock(read=MagicMock(return_value=MagicMock(author="AUTHOR")))
        configuration_class.return_value = configuration

        CookiecutterTemplateCompiler().compile_template(shell_name="shell",
                                                        template_path="template",
                                                        extra_context={},
                                                        running_on_same_folder=False)
        cookiecutter_mock.smarter_assert_called_once_with(
            cookiecutter,
            extra_context={"project_name": "shell", "full_name": "AUTHOR"},
            output_dir=os.path.curdir)
