from __future__ import annotations

import os

from attrs import define, field

from shellfoundry.utilities.config_reader import CloudShellConfigReader, Configuration
from shellfoundry.utilities.python_dependencies_packager import (
    PythonDependenciesPackager,
)


@define
class DistCommandExecutor:
    cloudshell_config_reader: Configuration = field(
        factory=lambda: Configuration(CloudShellConfigReader())
    )
    dependencies_packager: PythonDependenciesPackager = field(
        factory=PythonDependenciesPackager
    )

    def dist(self, enable_cs_repo: bool) -> None:
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
