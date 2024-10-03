# !/usr/bin/python
# -*- coding: utf-8 -*-

import os

import click

try:
    # Python 2.x version
    from urllib2 import HTTPError, URLError
except ImportError:
    # Python 3.x version
    from urllib.error import HTTPError, URLError

from shellfoundry.exceptions import FatalError
from shellfoundry.utilities.config_reader import CloudShellConfigReader, Configuration
from shellfoundry.utilities.installer import ShellInstaller
from shellfoundry.utilities.shell_config_reader import ShellConfigReader
from shellfoundry.utilities.shell_package import ShellPackage
from shellfoundry.utilities.shell_package_installer import ShellPackageInstaller


class InstallCommandExecutor(object):
    def __init__(
        self,
        cloudshell_config_reader=None,
        installer=None,
        shell_config_reader=None,
        shell_package_installer=None,
    ):
        self.cloudshell_config_reader = cloudshell_config_reader or Configuration(
            CloudShellConfigReader()
        )
        self.installer = installer or ShellInstaller()
        self.shell_config_reader = shell_config_reader or ShellConfigReader()
        self.shell_package_installer = (
            shell_package_installer or ShellPackageInstaller()
        )

    def install(self):
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
                "Failed to install shell. "
                "CloudShell responded with: '{}'".format(error)
            )
