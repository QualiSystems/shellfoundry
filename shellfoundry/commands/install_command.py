from urllib2 import HTTPError
import click
from shellfoundry.utilities.shell_config_reader import ShellConfigReader
from shellfoundry.utilities.config_reader import CloudShellConfigReader
from shellfoundry.utilities.installer import ShellInstaller


class InstallCommandExecutor(object):
    def __init__(self, cloudshell_config_reader=None, installer=None, shell_config_reader=None):
        self.cloudshell_config_reader = cloudshell_config_reader or CloudShellConfigReader()
        self.installer = installer or ShellInstaller()
        self.shell_config_reader = shell_config_reader or ShellConfigReader()

    def install(self):
        try:
            cloudshell_config = self.cloudshell_config_reader.read()
            shell_config = self.shell_config_reader.read()
            self.installer.install(shell_config.name, cloudshell_config)
        except HTTPError:
            click.echo(u'Login to CloudShell failed. Please verify the credentials in cloudshell_config.yml')

