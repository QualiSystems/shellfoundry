
import os

from shellfoundry.utilities.archive_creator import ArchiveCreator
from shellfoundry.utilities.python_dependencies_packager import PythonDependenciesPackager
from shellfoundry.utilities.shell_config_reader import ShellConfigReader
from shellfoundry.utilities.shell_package import ShellPackage


class DistCommandExecutor(object):
    def __init__(self, dependencies_packager=None):
        self.dependencies_packager = dependencies_packager or PythonDependenciesPackager()
        self.config_reader = ShellConfigReader()

    def dist(self):

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
            zip_file_path = os.path.join(dist_path, shell_name + ' offline requirements.zip')
        else:
            shell_name = self.config_reader.read().name
            zip_file_path = os.path.join(dist_path, shell_name + '_offline_requirements.zip')
        print shell_name
        print zip_file_path

        self.dependencies_packager.save_offline_dependencies(requirements_file_path, offline_requirements_path)
        ArchiveCreator.make_archive(zip_file_path, 'zip', offline_requirements_path)
