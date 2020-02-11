
import os

from shellfoundry.utilities.config_reader import Configuration, CloudShellConfigReader
from shellfoundry.utilities.python_dependencies_packager import PythonDependenciesPackager
from shellfoundry.utilities.shell_package import ShellPackage
from shellfoundry.utilities.archive_creator import ArchiveCreator


class DistCommandExecutor(object):

    def __init__(self, cloudshell_config_reader=None, dependencies_packager=None):
        self.cloudshell_config_reader = cloudshell_config_reader or Configuration(CloudShellConfigReader())
        self.dependencies_packager = dependencies_packager or PythonDependenciesPackager()

    def dist(self, enable_cs_repo):
        current_path = os.getcwd()
        dist_path = os.path.join(current_path, 'dist')
        offline_requirements_path = os.path.join(dist_path, 'offline_requirements')
        requirements_file_path = os.path.join(current_path, 'src', 'requirements.txt')
        shell_package = ShellPackage(current_path)
        if shell_package.is_tosca():
            import yaml
            with open(os.path.join(os.getcwd(), "shell-definition.yaml"), 'r') as f:
                shell = yaml.safe_load(f)
            shell_name = shell['metadata']['template_name']
        else:
            shell_name = self.config_reader.read().name
        zip_file_path = os.path.join(dist_path, shell_name + '_offline_requirements.zip')
        if enable_cs_repo:
            cs_server_address = self.cloudshell_config_reader.read().host
        else:
            cs_server_address = None
        self.dependencies_packager.save_offline_dependencies(requirements_file_path, offline_requirements_path,
                                                             cs_server_address)
        ArchiveCreator.make_archive(zip_file_path, 'zip', offline_requirements_path)
