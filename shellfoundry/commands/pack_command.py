import os
import click
from shellfoundry.exceptions import ShellYmlMissingException, WrongShellYmlException
from shellfoundry.utilities.package_builder import PackageBuilder
from shellfoundry.utilities.shell_config_reader import ShellConfigReader


class PackCommandExecutor(object):
    def __init__(self):
        self.config_reader = ShellConfigReader()
        self.package_builder = PackageBuilder()

    def pack(self):
        try:
            config = self.config_reader.read()
            current_path = os.getcwd()
            self.package_builder.build_package(current_path, config.name, config.driver_name)
        except ShellYmlMissingException:
            click.echo(u'shell.yml file is missing')
        except WrongShellYmlException:
            click.echo(u'shell.yml format is wrong')

