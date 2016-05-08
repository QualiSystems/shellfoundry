import os
import unittest
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
        self.assertTrue(os.path.exists(u'C:\\work\\GitHub\\aws\\amazon_web_services\aws.zip'))
