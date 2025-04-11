from __future__ import annotations

import os
from typing import TYPE_CHECKING

import click

from shellfoundry.utilities.cloudshell_api.client_wrapper import CloudShellClient

if TYPE_CHECKING:
    from shellfoundry.models.install_config import InstallConfig


class ShellInstaller:
    @staticmethod
    def install(package_name: str, config: InstallConfig):
        """Installs package according to cloudshell."""
        package_full_path = os.path.join(os.getcwd(), "dist", f"{package_name}.zip")
        click.echo(
            f"Installing package {package_full_path}"
            f" into CloudShell at http://{config.host}:{config.port}"
        )

        client = CloudShellClient(cs_config=config).create_client()
        client.import_package(package_full_path)
