#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
from os import path

import click

from shellfoundry.utilities.config_reader import CloudShellConfigReader, Configuration
from shellfoundry.utilities.driver_generator import DriverGenerator
from shellfoundry.utilities.shell_package import ShellPackage


class GenerateCommandExecutor(object):
    def __init__(self, cloudshell_config_reader=None, driver_generator=None):
        self.cloudshell_config_reader = cloudshell_config_reader or Configuration(
            CloudShellConfigReader()
        )
        self.driver_generator = driver_generator or DriverGenerator()

    def generate(self):
        """Generates Python driver by connecting to CloudShell server."""
        current_path = os.getcwd()
        shell_package = ShellPackage(current_path)
        if not shell_package.is_tosca():
            click.echo("Code generation supported in TOSCA based shells only", err=True)
            return

        shell_name = shell_package.get_name_from_definition()
        shell_filename = shell_name + ".zip"
        package_full_path = path.join(current_path, "dist", shell_filename)
        destination_path = path.join(current_path, "src")

        cloudshell_config = self.cloudshell_config_reader.read()

        click.echo("Connecting to Cloudshell server ...")

        self.driver_generator.generate_driver(
            cloudshell_config=cloudshell_config,
            destination_path=destination_path,
            package_full_path=package_full_path,
            shell_filename=shell_filename,
            shell_name=shell_name,
        )
