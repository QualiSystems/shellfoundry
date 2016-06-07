import os
import shutil
import zipfile

import click


class PackageBuilder(object):
    def __init__(self):
        pass

    def build_package(self, path, package_name):
        package_path = os.path.join(path, 'package')

        self._copy_metadata(package_path, path)
        self._copy_datamodel(package_path, path)
        self._copy_shellconfig(package_path, path)
        self._create_driver(package_path, path, package_name)
        zip_path = self._zip_package(package_path, path, package_name)
        click.echo(u'Shell package was successfully created:')
        click.echo(zip_path)

    @staticmethod
    def _copy_datamodel(package_path, path):
        src_file_path = os.path.join(path, 'datamodel', 'datamodel.xml')
        dest_dir_path = os.path.join(package_path, 'datamodel')
        PackageBuilder._copy_file(dest_dir_path, src_file_path)

    @staticmethod
    def _copy_file(dest_dir_path, src_file_path):
        if not os.path.exists(dest_dir_path):
            os.makedirs(dest_dir_path)
        shutil.copy(src_file_path, dest_dir_path)

    @staticmethod
    def _copy_shellconfig(package_path, path):
        src_file_path = os.path.join(path, 'datamodel', 'shellconfig.xml')
        if os.path.exists(src_file_path):
            dest_dir_path = os.path.join(package_path, 'Configuration')
            PackageBuilder._copy_file(dest_dir_path, src_file_path)

    @staticmethod
    def _create_driver(package_path, path, package_name):
        dir_to_zip = os.path.join(path, 'src')
        zip_file_path = os.path.join(package_path, 'Resource Drivers - Python', package_name + ' Driver')
        PackageBuilder._make_archive(zip_file_path, 'zip', dir_to_zip)

    @staticmethod
    def _zip_package(package_path, path, package_name):
        zip_file_path = os.path.join(path, 'dist', package_name)
        return PackageBuilder._make_archive(zip_file_path, 'zip', package_path)

    @staticmethod
    def _make_archive(output_filename, format, source_dir):
        """
        Creates archive in specified format recursively of source_dir
        Replaces shtutil.make_archive in order to be able to test with pyfakefs
        :param output_filename: Output archive file name. If directory does not exist, it will be created
        :param format: Archive format to be used. Currently only zip is supported
        :param source_dir: Directory to scan for archiving
        :return:
        """
        if os.path.splitext(output_filename)[1] == '':
            output_filename += '.zip'
        output_dir = os.path.dirname(output_filename)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        relroot = source_dir
        with zipfile.ZipFile(output_filename, "w", zipfile.ZIP_DEFLATED) as zip:
            for root, dirs, files in os.walk(source_dir):
                # add directory (needed for empty dirs)
                zip.write(root, os.path.relpath(root, relroot))
                for file in files:
                    filename = os.path.join(root, file)
                    if os.path.isfile(filename): # regular files only
                        arcname = os.path.join(os.path.relpath(root, relroot), file)
                        zip.write(filename, arcname)

        return output_filename

    def _copy_metadata(self, package_path, path):
        src_file_path = os.path.join(path, 'datamodel', 'metadata.xml')
        PackageBuilder._copy_file(package_path, src_file_path)
