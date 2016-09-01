import os
from urllib2 import HTTPError
import click
from shellfoundry.utilities.shell_config_reader import ShellConfigReader
from shellfoundry.utilities.config_reader import CloudShellConfigReader
from shellfoundry.utilities.installer import ShellInstaller
from shellfoundry.utilities.shell_package import ShellPackage
from shellfoundry.utilities.shell_package_installer import ShellPackageInstaller


class InstallCommandExecutor(object):
    def __init__(self, cloudshell_config_reader=None, installer=None, shell_config_reader=None,
                 shell_package_installer=None):
        self.cloudshell_config_reader = cloudshell_config_reader or CloudShellConfigReader()
        self.installer = installer or ShellInstaller()
        self.shell_config_reader = shell_config_reader or ShellConfigReader()
        self.shell_package_installer = shell_package_installer or ShellPackageInstaller()

    def install(self):
        current_path = os.getcwd()
        shell_package = ShellPackage(current_path)
        if shell_package.is_tosca():
            self.shell_package_installer.install(current_path)
        else:
            self._install_old_school_shell()

    def _install_old_school_shell(self):
        try:
            cloudshell_config = self.cloudshell_config_reader.read()
            shell_config = self.shell_config_reader.read()
            self.installer.install(shell_config.name, cloudshell_config)
        except HTTPError:
            click.echo(u'Login to CloudShell failed. Please verify the credentials in cloudshell_config.yml')

