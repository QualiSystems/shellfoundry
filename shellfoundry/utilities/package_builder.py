import os
import shutil


class PackageBuilder(object):
    def __init__(self):
        pass

    def build_package(self, path, package_name):
        package_path = os.path.join(path, 'package')

        self._copy_datamodel(package_path, path)
        self._copy_shellconfig(package_path, path)
        self._create_driver(package_path, path, package_name)
        self._zip_package(package_path, path, package_name)

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
        dest_dir_path = os.path.join(package_path, 'Configuration')
        PackageBuilder._copy_file(dest_dir_path, src_file_path)

    @staticmethod
    def _create_driver(package_path, path, package_name):
        dir_to_zip = os.path.join(path, 'src')
        zip_file_path = os.path.join(package_path, 'Resource Drivers - Python', package_name + ' Driver')
        shutil.make_archive(zip_file_path, 'zip', dir_to_zip)

    @staticmethod
    def _zip_package(package_path, path, package_name):
        zip_file_path = os.path.join(path, package_name)
        shutil.make_archive(zip_file_path, 'zip', package_path)
