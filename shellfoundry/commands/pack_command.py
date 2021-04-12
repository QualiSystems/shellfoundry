#!/usr/bin/python
# -*- coding: utf-8 -*-

import os

import click

from shellfoundry.exceptions import ShellYmlMissingException, WrongShellYmlException
from shellfoundry.utilities.package_builder import PackageBuilder
from shellfoundry.utilities.shell_config_reader import ShellConfigReader
from shellfoundry.utilities.shell_package import ShellPackage
from shellfoundry.utilities.shell_package_builder import ShellPackageBuilder


class PackCommandExecutor(object):
    def __init__(self):
        self.config_reader = ShellConfigReader()
        self.package_builder = PackageBuilder()
        self.shell_package_builder = ShellPackageBuilder()

    def pack(self):

        current_path = os.getcwd()

        shell_package = ShellPackage(current_path)
        if shell_package.is_layer_one():
            click.secho(
                "Packaging a L1 shell directly via shellfoundry is not supported.",
                fg="yellow",
            )
        elif shell_package.is_tosca():
            self.shell_package_builder.pack(current_path)
        else:
            self._pack_old_school_shell(current_path)

    def _pack_old_school_shell(self, current_path):
        try:
            config = self.config_reader.read()
            self.package_builder.build_package(
                current_path, config.name, config.driver_name
            )
        except ShellYmlMissingException:
            click.echo("shell.yml file is missing")
        except WrongShellYmlException:
            click.echo("shell.yml format is wrong")
