#!/usr/bin/python
# -*- coding: utf-8 -*-

import os

from cookiecutter.main import cookiecutter
from shellfoundry.utilities.config_reader import Configuration, CloudShellConfigReader


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
