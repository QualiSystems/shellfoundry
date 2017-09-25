#!/usr/bin/python
# -*- coding: utf-8 -*-

import os

from cookiecutter.main import cookiecutter
from shellfoundry.commands.config_command import ConfigCommandExecutor
from shellfoundry.utilities.config_reader import Configuration, AUTHOR


class CookiecutterTemplateCompiler(object):
    def __init__(self):
        pass

    def compile_template(self, shell_name, template_path, extra_context, running_on_same_folder):

        extra_context["project_name"] = shell_name
        config_path = ConfigCommandExecutor._get_config_file_path(is_global_flag=True)
        extra_context["full_name"] = Configuration.get_configuration_attr(config_path=config_path,
                                                                          attr_name=AUTHOR)

        if running_on_same_folder:
            output_dir = os.path.pardir
        else:
            output_dir = os.path.curdir

        cookiecutter(template_path, no_input=True,
                     extra_context=extra_context,
                     overwrite_if_exists=False, output_dir=output_dir)
