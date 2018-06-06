#!/usr/bin/python
# -*- coding: utf-8 -*-

import os

from cookiecutter.main import cookiecutter
from shellfoundry.utilities.config_reader import Configuration, CloudShellConfigReader
from shellfoundry.utilities.constants import TEMPLATE_INFO_FILE


class CookiecutterTemplateCompiler(object):
    def __init__(self):
        self.cloudshell_config_reader = Configuration(CloudShellConfigReader())

    def compile_template(self, shell_name, template_path, extra_context, running_on_same_folder):

        extra_context["project_name"] = shell_name
        extra_context["full_name"] = self.cloudshell_config_reader.read().author

        if running_on_same_folder:
            output_dir = os.path.pardir
        else:
            output_dir = os.path.curdir

        cookiecutter(template_path, no_input=True,
                     extra_context=extra_context,
                     overwrite_if_exists=False, output_dir=output_dir)

        # self._remove_template_info_file(output_dir)

    @staticmethod
    def _remove_template_info_file(shell_path):
        """ Remove template info file from shell structure """

        template_info_file_path = os.path.join(shell_path, TEMPLATE_INFO_FILE)
        if os.path.exists(template_info_file_path):
            os.remove(template_info_file_path)
