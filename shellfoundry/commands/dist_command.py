#!/usr/bin/python
# -*- coding: utf-8 -*-

import os

from shellfoundry.utilities.config_reader import CloudShellConfigReader, Configuration
from shellfoundry.utilities.python_dependencies_packager import (
    PythonDependenciesPackager,
)


class DistCommandExecutor(object):
    def __init__(self, cloudshell_config_reader=None, dependencies_packager=None):
        self.cloudshell_config_reader = cloudshell_config_reader or Configuration(
            CloudShellConfigReader()
        )
        self.dependencies_packager = (
            dependencies_packager or PythonDependenciesPackager()
        )

    def dist(self, enable_cs_repo):
        """Creates offline dependencies archive."""
        current_path = os.getcwd()
        requirements_path = os.path.join(current_path, "src", "requirements.txt")
        dest_path = os.path.join(current_path, "dist", "offline_requirements")

        if enable_cs_repo:
            cs_server_address = self.cloudshell_config_reader.read().host
        else:
            cs_server_address = None

        self.dependencies_packager.save_offline_dependencies(
            requirements_path, dest_path, cs_server_address
        )
