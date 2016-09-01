import os

from shellfoundry.utilities.python_dependencies_packager import PythonDependenciesPackager


class DistCommandExecutor(object):
    def __init__(self, dependencies_packager=None):
        self.dependencies_packager = dependencies_packager or PythonDependenciesPackager()

    def dist(self):
        current_path = os.getcwd()

        requirements_path = os.path.join(current_path, 'src', 'requirements.txt')
        dest_path = os.path.join(current_path, 'dist', 'offline_requirements')

        self.dependencies_packager.save_offline_dependencies(requirements_path, dest_path)
