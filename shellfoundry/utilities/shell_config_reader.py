from __future__ import annotations

import os

import yaml
from attrs import define

from shellfoundry.exceptions import ShellYmlMissingException, WrongShellYmlException

AUTHOR = "author"
DESCRIPTION = "description"
DRIVER_NAME = "driver_name"
EMAIL = "email"
NAME = "name"
SHELL = "shell"
VERSION = "version"


@define
class ProjectConfig:
    name: str = ""
    author: str = ""
    email: str = ""
    description: str = ""
    version: str = ""
    driver_name: str = ""


class ShellConfigReader:
    @staticmethod
    def read():
        config_path = os.path.join(os.getcwd(), "shell.yml")

        if not os.path.isfile(config_path):
            raise ShellYmlMissingException("shell.yml is missing")

        with open(config_path, encoding="utf8") as stream:
            config = yaml.safe_load(stream.read())

        if not config or SHELL not in config:
            raise WrongShellYmlException("shell section is missing in shell.yml")

        install_config = config[SHELL]
        if install_config:
            return ProjectConfig(
                name=install_config.get(NAME, ""),
                author=install_config.get(AUTHOR, ""),
                email=install_config.get(EMAIL, ""),
                description=install_config.get(DESCRIPTION, ""),
                version=install_config.get(VERSION, ""),
                driver_name=install_config.get(DRIVER_NAME, ""),
            )
        else:
            return ProjectConfig()
