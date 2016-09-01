import os
import click
import shutil

import yaml

from shellfoundry.utilities.archive_creator import ArchiveCreator
from shellfoundry.utilities.shell_package import ShellPackage
from shellfoundry.utilities.temp_dir_context import TempDirContext


class ShellPackageBuilder(object):

    def pack(self, path):
        """
        Creates TOSCA based Shell package
        :return:
        """
        shell_package = ShellPackage(path)
        shell_name = shell_package.get_shell_name()
        with TempDirContext(shell_name) as package_path:

            self._copy_tosca_meta(package_path, '')
            tosca_meta = self._read_tosca_meta(path)

            shell_definition_path = tosca_meta['Entry-Definitions']

            self._copy_shell_definition(package_path, '', shell_definition_path)
            self._create_driver('', os.curdir, shell_name)

            with open(shell_definition_path) as shell_definition_file:
                shell_definition = yaml.load(shell_definition_file)
                for node_type in shell_definition['node_types'].values():
                    if 'artifacts' not in node_type:
                        continue
                    for artifact in node_type['artifacts'].values():
                        self._copy_artifact(artifact['file'], package_path)

            zip_path = self._zip_package(package_path, '', shell_name)

            click.echo(u'Shell package was successfully created: ' + zip_path)

    def _copy_artifact(self, artifact_path, package_path):
        if os.path.exists(artifact_path):
            click.echo('Adding artifact to shell package: ' + artifact_path)
            self._copy_file(src_file_path=artifact_path, dest_dir_path=package_path)
        else:
            click.echo('Missing artifact not added to shell package: ' + artifact_path)

    def _read_tosca_meta(self, path):
        tosca_meta = {}
        shell_package = ShellPackage(path)
        with open(shell_package.get_metadata_path()) as meta_file:
            for meta_line in meta_file:
                (key, val) = meta_line.split(':')
                tosca_meta[key] = val.strip()
        return tosca_meta

    def _copy_shell_icon(self, package_path, path):
        self._copy_file(
            src_file_path=os.path.join(path, 'shell-icon.png'),
            dest_dir_path=package_path)

    def _copy_shell_definition(self, package_path, path, shell_definition):
        self._copy_file(
            src_file_path=os.path.join(path, shell_definition),
            dest_dir_path=package_path)

    def _copy_tosca_meta(self, package_path, path):
        shell_package = ShellPackage(path)
        self._copy_file(
            src_file_path=shell_package.get_metadata_path(),
            dest_dir_path=os.path.join(package_path, 'TOSCA-Metadata'))

    @staticmethod
    def _create_driver(path, package_path, shell_name):
        dir_to_zip = os.path.join(path, 'src')
        driver_name = shell_name + 'Driver'
        zip_file_path = os.path.join(package_path, driver_name)
        ArchiveCreator.make_archive(zip_file_path, 'zip', dir_to_zip)

    @staticmethod
    def _copy_file(src_file_path, dest_dir_path):
        if not os.path.exists(dest_dir_path):
            os.makedirs(dest_dir_path)
        shutil.copy(src_file_path, dest_dir_path)

    @staticmethod
    def _zip_package(package_path, path, package_name):
        zip_file_path = os.path.join(path, 'dist', package_name)
        return ArchiveCreator.make_archive(zip_file_path, 'zip', package_path)
