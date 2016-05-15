import os
from pyfakefs import fake_filesystem_unittest
from shellfoundry.package_builder import PackageBuilder


class TestPackageBuilder(fake_filesystem_unittest.TestCase):
    def setUp(self):
        self.setUpPyfakefs()

    # @unittest.skip('fake file system is not working as expected')
    def test_build_package_package_created(self):
        # Arrange
        self.fs.CreateFile(u'C:\\work\\aws\\amazon_web_services\\datamodel\\datamodel.xml', contents='')
        self.fs.CreateFile(u'C:\\work\\aws\\amazon_web_services\\datamodel\\shellconfig.xml', contents='')
        self.fs.CreateFile(u'C:\\work\\aws\\amazon_web_services\\src\\driver.py', contents='')
        builder = PackageBuilder()

        # Act
        builder.build_package(u'C:\\work\\aws\\amazon_web_services', 'aws')

        # Assert
        self.assertFileExists(u'C:\\work\\aws\\amazon_web_services\\package\\datamodel\datamodel.xml')
        self.assertFileExists(u'C:\\work\\aws\\amazon_web_services\\package\\Configuration\shellconfig.xml')
        self.assertFileExists(u'C:\\work\\aws\\amazon_web_services\\package\\Resource Drivers - Python\\aws Driver.zip')
        self.assertFileExists(u'C:\\work\\aws\\amazon_web_services\\aws.zip')

    def assertFileExists(self, file_path):
        self.assertTrue(os.path.exists(file_path), msg='File {0} does not exist'.format(file_path))





