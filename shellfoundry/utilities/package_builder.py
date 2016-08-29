import codecs
import os
import shutil
import click
import mimetypes

from shellfoundry.utilities.archive_creator import ArchiveCreator
from shellfoundry.utilities.shell_datamodel_merger import ShellDataModelMerger


class PackageBuilder(object):
    def __init__(self):
        pass

    def build_package(self, path, package_name, driver_name):
        package_path = os.path.join(path, 'package')
        self._copy_metadata(package_path, path)
        self._copy_datamodel(package_path, path)
        self._copy_images(package_path, path)
        self._copy_shellconfig(package_path, path)
        self._create_driver(package_path, path, driver_name)
        zip_path = self._zip_package(package_path, path, package_name)
        shutil.rmtree(path=package_path, ignore_errors=True)
        click.echo(u'Shell package was successfully created:')
        click.echo(zip_path)

    def _copy_metadata(self, package_path, path):
        src_file_path = os.path.join(path, 'datamodel', 'metadata.xml')
        PackageBuilder._copy_file(package_path, src_file_path)

    @staticmethod
    def _get_file_content_as_string(path):
        with codecs.open(path, 'r', encoding='utf8') as f:
            text = f.read()
        return text

    @staticmethod
    def _save_to_utf_file(content, dest_path):
        with codecs.open(dest_path, "w", "utf-8-sig") as f:
            f.write(content)

    @staticmethod
    def _copy_datamodel(package_path, path):
        shell_model_path = os.path.join(path, 'datamodel', 'shell_model.xml')
        src_dm_file_path = os.path.join(path, 'datamodel', 'datamodel.xml')
        dest_dir_path = os.path.join(package_path, 'DataModel')

        if os.path.exists(shell_model_path):
            shell_model = PackageBuilder._get_file_content_as_string(shell_model_path)
            dm = PackageBuilder._get_file_content_as_string(src_dm_file_path)
            merger = ShellDataModelMerger()
            merged_dm  = merger.merge_shell_model(dm, shell_model)
            if not os.path.exists(dest_dir_path):
                os.makedirs(dest_dir_path)
            PackageBuilder._save_to_utf_file(merged_dm, os.path.join(dest_dir_path, 'datamodel.xml'))

        else:
            PackageBuilder._copy_file(dest_dir_path, src_dm_file_path)

    @staticmethod
    def _is_image(file):
        type, encoding = mimetypes.guess_type(file)
        return type and "image" in type

    @staticmethod
    def _copy_images(package_path, path):
        dest_dir_path = os.path.join(package_path, 'DataModel')
        datamodel_dir = os.path.join(path, 'datamodel')
        for root, _, files in os.walk(datamodel_dir):
            images = [dir_file for dir_file in files if PackageBuilder._is_image(dir_file)]
            for image in images:
                PackageBuilder._copy_file(dest_dir_path,  os.path.join(root, image))

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
    def _create_driver(package_path, path, driver_name):
        dir_to_zip = os.path.join(path, 'src')
        zip_file_path = os.path.join(package_path, 'Resource Drivers - Python', driver_name)
        ArchiveCreator.make_archive(zip_file_path, 'zip', dir_to_zip)

    @staticmethod
    def _zip_package(package_path, path, package_name):
        zip_file_path = os.path.join(path, 'dist', package_name)
        return ArchiveCreator.make_archive(zip_file_path, 'zip', package_path)

