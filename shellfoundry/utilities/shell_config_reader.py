#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
from io import open

import yaml

from shellfoundry.exceptions import ShellYmlMissingException, WrongShellYmlException

VERSION = "version"
DESCRIPTION = "description"
EMAIL = "email"
AUTHOR = "author"
NAME = "name"
SHELL = "shell"
DRIVER_NAME = "driver_name"


class ProjectConfig(object):
    def __init__(self, name, author, email, description, version, driver_name):
        self.version = version
        self.description = description
        self.email = email
        self.author = author
        self.name = name
        self.driver_name = driver_name


class ShellConfigReader(object):
    def read(self):
        config_path = os.path.join(os.getcwd(), "shell.yml")

        if not os.path.isfile(config_path):
            raise ShellYmlMissingException("shell.yml is missing")

        with open(config_path, encoding="utf8") as stream:
            config = yaml.safe_load(stream.read())

        if not config or SHELL not in config:
            raise WrongShellYmlException("shell section is missing in shell.yml")

        install_config = config[SHELL]

        name = self._get_with_default(install_config, NAME, "")
        author = self._get_with_default(install_config, AUTHOR, "")
        email = self._get_with_default(install_config, EMAIL, "")
        description = self._get_with_default(install_config, DESCRIPTION, "")
        version = self._get_with_default(install_config, VERSION, "")
        driver_name = self._get_with_default(install_config, DRIVER_NAME, "")

        return ProjectConfig(name, author, email, description, version, driver_name)

    @staticmethod
    def _get_with_default(install_config, parameter_name, default_value):
        return (
            install_config[parameter_name]
            if install_config and parameter_name in install_config
            else default_value
        )
