import os
from shellfoundry.package_builder import PackageBuilder
from shellfoundry.shell_config_reader import ShellConfigReader


class PackCommandExecutor(object):
    def __init__(self):
        self.config_reader = ShellConfigReader()
        self.package_builder = PackageBuilder()

    def pack(self):
        config = self.config_reader.read()
        current_path = os.getcwd()
        self.package_builder.build_package(current_path, config.name)

