import os
import click
import shutil

from shellfoundry.utilities.archive_creator import ArchiveCreator


class ShellPackageBuilder(object):

    def is_tosca_based_shell(self, path):
        """
        Determines whether a shell is a TOSCA based shell
        :param path: Path to shell
        :return:
        :rtype: bool
        """
        return os.path.exists(self._get_tosca_meta_path(path))

    def pack(self):
        package_path = 'shell-package'

        self._copy_tosca_meta(package_path, '')
        self._copy_shell_definition(package_path, '')
        self._copy_shell_icon(package_path, '')
        self._create_driver('', package_path)
        zip_path = self._zip_package(package_path, '', 'shell-package')

        if os.path.exists(package_path):
            shutil.rmtree(path=package_path, ignore_errors=True)

        click.echo(u'Shell package was successfully created:')
        click.echo(zip_path)

    def _copy_shell_icon(self, package_path, path):
        self._copy_file(
            src_file_path=os.path.join(path, 'shell-icon.png'),
            dest_dir_path=package_path)

    def _copy_shell_definition(self, package_path, path):
        self._copy_file(
            src_file_path=os.path.join(path, 'shell-definition.yml'),
            dest_dir_path=package_path)

    def _copy_tosca_meta(self, package_path, path):
        self._copy_file(
            src_file_path=self._get_tosca_meta_path(path),
            dest_dir_path=os.path.join(package_path, 'TOSCA-Metadata'))

    @staticmethod
    def _get_tosca_meta_path(path):
        return os.path.join(path, 'TOSCA-Metadata', 'TOSCA.meta')

    @staticmethod
    def _create_driver(path, package_path):
        dir_to_zip = os.path.join(path, 'src')
        zip_file_path = os.path.join(package_path, 'shell-driver')
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
