import codecs
import os
import shutil
import zipfile

import click
import mimetypes

import re
from datetime import datetime
import xml.etree.ElementTree as etree
from version_utilities import VersionUtilities

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
    def _save_to_file(content, dest_path):
        with codecs.open(dest_path, "w") as f:
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
            merged_dm = merger.merge_shell_model(dm, shell_model)
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
        drivermetadata_path = os.path.join(dir_to_zip, 'drivermetadata.xml')
        version = PackageBuilder._update_driver_version(drivermetadata_path)
        zip_file_path = os.path.join(package_path, 'Resource Drivers - Python', driver_name)
        PackageBuilder._make_archive(zip_file_path, 'zip', dir_to_zip)
        if version:  # version was replaced
            PackageBuilder._update_driver_version(drivermetadata_path, version)

    @staticmethod
    def _parse_xml(xml_string):
        parser = etree.XMLParser(encoding='utf-8')
        return etree.fromstring(xml_string, parser)

    @staticmethod
    def _update_driver_version(metadata_path, version=''):
        if not os.path.isfile(metadata_path):
            return None

        metadata = PackageBuilder._get_file_content_as_string(metadata_path)
        metadata_xml = PackageBuilder._parse_xml(metadata)
        curver = metadata_xml.get("Version")

        if re.match('\d+\.\d+\.\*', curver):
            build_and_revision = VersionUtilities.get_timestamped_build_and_revision()
            newver = curver.replace('*', build_and_revision)
            metadata_xml.set('Version', newver)
            PackageBuilder._save_to_file(etree.tostring(metadata_xml), metadata_path)
            return curver

        elif version:
            metadata_xml.set('Version', version)
            PackageBuilder._save_to_file(etree.tostring(metadata_xml), metadata_path)
            return None

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
                    if os.path.isfile(filename):  # regular files only
                        arcname = os.path.join(os.path.relpath(root, relroot), file)
                        zip.write(filename, arcname)

        return output_filename
