from __future__ import annotations

import os
from urllib.error import HTTPError, URLError

import click
from attrs import define, field

from shellfoundry.exceptions import FatalError
from shellfoundry.utilities.config_reader import CloudShellConfigReader, Configuration
from shellfoundry.utilities.installer import ShellInstaller
from shellfoundry.utilities.shell_config_reader import ShellConfigReader
from shellfoundry.utilities.shell_package import ShellPackage
from shellfoundry.utilities.shell_package_installer import ShellPackageInstaller


@define
class InstallCommandExecutor:
    cloudshell_config_reader: Configuration = field(
        factory=lambda: Configuration(CloudShellConfigReader())
    )
    installer: ShellInstaller = field(factory=ShellInstaller)
    shell_config_reader: ShellConfigReader = field(factory=ShellConfigReader)
    shell_package_installer: ShellPackageInstaller = field(
        factory=ShellPackageInstaller
    )

    def install(self):
        """Install Shell."""
        current_path = os.getcwd()
        shell_package = ShellPackage(current_path)
        if shell_package.is_layer_one():
            click.secho(
                "Installing a L1 shell directly via shellfoundry is not supported. "
                "Please follow the L1 shell import procedure described in help.quali.com.",  # noqa: E501
                fg="yellow",
            )
        else:
            if shell_package.is_tosca():
                self.shell_package_installer.install(current_path)
            else:
                self._install_old_school_shell()
            click.secho("Successfully installed shell", fg="green")

    def _install_old_school_shell(self):
        """Install Shell first generation."""
        error = None
        try:
            cloudshell_config = self.cloudshell_config_reader.read()
            shell_config = self.shell_config_reader.read()
            self.installer.install(shell_config.name, cloudshell_config)
        except HTTPError as e:
            if e.code == 401:
                raise FatalError(
                    "Login to CloudShell failed. "
                    "Please verify the credentials in the config"
                )
            error = str(e)
        except URLError:
            raise FatalError(
                "Connection to CloudShell Server failed. "
                "Please make sure it is up and running properly."
            )
        except Exception as e:
            error = str(e)

        if error:
            raise FatalError(
                f"Failed to install shell. " f"CloudShell responded with: '{error}'"
            )
