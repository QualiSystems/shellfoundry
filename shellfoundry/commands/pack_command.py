import os
import click
from shellfoundry.exceptions import ShellYmlMissingException, WrongShellYmlException
from shellfoundry.utilities.package_builder import PackageBuilder
from shellfoundry.utilities.python_depedencies_packager import PythonDependenciesPackager
from shellfoundry.utilities.shell_config_reader import ShellConfigReader


class PackCommandExecutor(object):

    def __init__(self):
        self.config_reader = ShellConfigReader()
        self.package_builder = PackageBuilder()
        self.dependencies_packager = PythonDependenciesPackager()

    def pack(self):
        try:
            config = self.config_reader.read()
            current_path = os.getcwd()
            self.package_builder.build_package(current_path, config.name, config.driver_name)
            requirements_path = os.path.join(current_path, 'src', 'requirements.txt')
            dest_path = os.path.join(current_path, 'dist', 'offline_requirements')

            self.dependencies_packager.save_offline_dependencies(requirements_path, dest_path)
        except ShellYmlMissingException:
            click.echo(u'shell.yml file is missing')
        except WrongShellYmlException:
            click.echo(u'shell.yml format is wrong')

