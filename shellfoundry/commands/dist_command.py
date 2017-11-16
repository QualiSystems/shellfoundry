
import os

from shellfoundry.utilities.archive_creator import ArchiveCreator
from shellfoundry.utilities.python_dependencies_packager import PythonDependenciesPackager
from shellfoundry.utilities.shell_config_reader import ShellConfigReader


class DistCommandExecutor(object):
    def __init__(self, dependencies_packager=None):
        self.dependencies_packager = dependencies_packager or PythonDependenciesPackager()
        self.config_reader = ShellConfigReader()

    def dist(self):

        current_path = os.getcwd()
        dist_path = os.path.join(current_path, 'dist')
        offline_requirements_path = os.path.join(dist_path, 'offline_requirements')
        requirements_file_path = os.path.join(current_path, 'src', 'requirements.txt')
        zip_file_path = os.path.join(dist_path, self.config_reader.read().name + '_offline_requirements.zip')

        self.dependencies_packager.save_offline_dependencies(requirements_file_path, offline_requirements_path)
        ArchiveCreator.make_archive(zip_file_path, 'zip', offline_requirements_path)
