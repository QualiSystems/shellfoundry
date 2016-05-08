import os
from shutil import copyfile, copytree
import zipfile
from qpm.packaging.driver_packager import zip_dir


class PackageBuilder(object):
    def __init__(self):
        pass

    def build_package(self, path, package_name):
        package_path = os.path.join(path, 'package')

        self._copy_datamodel(package_path, path)
        self._copy_shellconfig(package_path, path)
        self._copy_driver(package_path, path, package_name)

    @staticmethod
    def _copy_datamodel(package_path, path):
        src_file_path = os.path.join(path, ['datamodel', 'datamodel.xml'])
        dest_dir_path = os.path.join(package_path, 'datamodel')
        copyfile(src_file_path, dest_dir_path)

    @staticmethod
    def _copy_shellconfig(package_path, path):
        src_file_path = os.path.join(path, ['datamodel', 'shellconfig.xml'])
        dest_dir_path = os.path.join(package_path, 'Configuration')
        copyfile(src_file_path, dest_dir_path)

    @staticmethod
    def _copy_driver(package_path, path, package_name):
        src_dir_path = os.path.join(path, 'src')
        dest_dir_path = os.path.join(package_path, 'Resource Drivers - Python')
        copytree(src_dir_path, dest_dir_path)
        zip_file = zipfile.ZipFile(os.path.join(dest_dir_path, package_name + '.zip'), 'w')
        zip_dir(dest_dir_path, zip_file, False, True)
        zip_file.close()



