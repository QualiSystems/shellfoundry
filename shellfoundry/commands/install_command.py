from shellfoundry.utilities.config_reader import CloudShellConfigReader
from shellfoundry.utilities.installer import ShellInstaller


class InstallCommandExecutor(object):
    def __init__(self):
        self.config_reader = CloudShellConfigReader()
        self.installer = ShellInstaller()

    def install(self):
        project = self.config_reader.read()
        self.installer.install(project.name, project.install)
