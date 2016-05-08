import os
import unittest
from shutil import copy

from pyfakefs import fake_filesystem_unittest
from shellfoundry.package_builder import PackageBuilder


class TestPackageBuilder(fake_filesystem_unittest.TestCase):
    def setUp(self):
        self.setUpPyfakefs()

    def test_build_package(self):
        # Arrange
        self.fs.CreateFile(u'C:\\work\\GitHub\\aws\\amazon_web_services\\datamodel\\datamodel.xml', contents='')
        self.fs.CreateFile(u'C:\\work\\GitHub\\aws\\amazon_web_services\\datamodel\\shellconfig.xml', contents='')
        self.fs.CreateFile(u'C:\\work\\GitHub\\aws\\amazon_web_services\\src\\driver.py', contents='')
        builder = PackageBuilder()

        # Act
        builder.build_package(u'C:\\work\\GitHub\\aws\\amazon_web_services', 'aws')

        # Assert
        self.assertFileExists(u'C:\\work\\GitHub\\aws\\amazon_web_services\package\\datamodel\datamodel.xml')
        self.assertFileExists(u'C:\\work\\GitHub\\aws\\amazon_web_services\package\\Configuration\shellconfig.xml')
        self.assertFileExists(
            u'C:\\work\\GitHub\\aws\\amazon_web_services\package\\Resource Drivers - Python\\aws Driver.zip')

    def test_copy(self):
        self.fs.CreateFile(u'C:\\source\\file.txt', contents='')
        os.makedirs(u'C:\destination')
        copy(u'C:\\source\\file.txt', u'C:\destination')

        self.assertFileExists(u'C:\destination\\file.txt')

    def test_zip(self):
        self.fs.CreateFile(u'C:\\source\\file.txt', contents='')

        os.makedirs(u'C:\destination')
        copy(u'C:\\source\\file.txt', u'C:\destination')

        self.assertFileExists(u'C:\destination\\file.txt')


    def assertFileExists(self, file_path):
        self.assertTrue(os.path.exists(file_path))

