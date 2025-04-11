from __future__ import annotations

import zipfile
from os import path
from typing import TYPE_CHECKING

import click
from cloudshell.rest.api import _get_api_url
from requests import post

from shellfoundry.utilities.cloudshell_api.client_wrapper import CloudShellClient
from shellfoundry.utilities.temp_dir_context import TempDirContext

if TYPE_CHECKING:
    from cloudshell.rest.api import PackagingRestApiClient

    from shellfoundry.models.install_config import InstallConfig


class DriverGenerator:
    def generate_driver(
        self,
        cloudshell_config: InstallConfig,
        destination_path: str,
        package_full_path: str,
        shell_filename: str,
        shell_name: str,
    ) -> None:
        """Generates Python data model by connecting to Cloudshell server."""
        client = CloudShellClient(cs_config=cloudshell_config).create_client()
        self._generate_driver_data_model(
            client=client,
            cloudshell_config=cloudshell_config,
            destination_path=destination_path,
            package_full_path=package_full_path,
            shell_filename=shell_filename,
            shell_name=shell_name,
        )

    @staticmethod
    def _generate_driver_data_model(
        client: PackagingRestApiClient,
        cloudshell_config: InstallConfig,
        destination_path: str,
        package_full_path: str,
        shell_filename: str,
        shell_name: str,
    ) -> None:
        """Generates driver data model."""
        base_api_url = _get_api_url(cloudshell_config.host, cloudshell_config.port)
        url = f"{base_api_url}ShellDrivers/Generate"
        response = post(
            url,
            files={path.basename(shell_filename): open(package_full_path, "rb")},
            headers=client._headers,
        )

        if response.status_code != 200:
            click.echo(
                message=f"Code generation failed with code {response.status_code} "
                f"and error {response.text}",
                err=True,
            )
            return

        click.echo("Extracting data model ...")
        with TempDirContext(remove_dir_on_error=False, prefix=shell_name) as temp_dir:
            generated_zip = path.join(temp_dir, shell_filename)
            click.echo(f"Writing temporary file {generated_zip}")
            with open(generated_zip, "wb") as driver_file:
                driver_file.write(response.content)

            click.echo(f"Extracting generated code at {destination_path}")
            with zipfile.ZipFile(generated_zip) as zf:
                zf.extractall(destination_path)
