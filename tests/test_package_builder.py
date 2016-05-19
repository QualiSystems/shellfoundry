import unittest
from pyfakefs import fake_filesystem_unittest
from shellfoundry.package_builder import PackageBuilder
from asserts import *


class TestPackageBuilder(fake_filesystem_unittest.TestCase):
    def setUp(self):
        self.setUpPyfakefs()

    @unittest.skip('make_archive does not support fakefs')
    def test_build_package_package_created(self):
        # Arrange
        self.fs.CreateFile('work/aws/amazon_web_services/datamodel/datamodel.xml', contents='')
        self.fs.CreateFile('work/aws/amazon_web_services/datamodel/shellconfig.xml', contents='')
        self.fs.CreateFile('work/aws/amazon_web_services/src/driver.py', contents='')
        builder = PackageBuilder()

        # Act
        builder.build_package('work/aws/amazon_web_services', 'aws')

        # Assert
        assertFileExists(self, 'work/aws/amazon_web_services/package/datamodel/datamodel.xml')
        assertFileExists(self, 'work/aws/amazon_web_services/package/Configuration/shellconfig.xml')
        assertFileExists(self, 'work/aws/amazon_web_services/package/Resource Drivers - Python/aws Driver.zip')
        assertFileExists(self, 'work/aws/amazon_web_services/aws.zip')

    def assertFileExists(self, file_path):
        self.assertTrue(os.path.exists(file_path), msg='File {0} does not exist'.format(file_path))






