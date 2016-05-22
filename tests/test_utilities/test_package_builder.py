from pyfakefs import fake_filesystem_unittest
from tests.asserts import *
from shellfoundry.utilities.package_builder import PackageBuilder


class TestPackageBuilder(fake_filesystem_unittest.TestCase):
    def setUp(self):
        self.setUpPyfakefs()

    def test_build_package_package_created(self):
        # Arrange
        self.fs.CreateFile('work/aws/amazon_web_services/datamodel/datamodel.xml', contents='')
        self.fs.CreateFile('work/aws/amazon_web_services/datamodel/shellconfig.xml', contents='')
        self.fs.CreateFile('work/aws/amazon_web_services/src/driver.py', contents='')
        os.chdir('work')
        builder = PackageBuilder()

        # Act
        builder.build_package('aws/amazon_web_services', 'aws')

        # Assert
        assertFileExists(self, 'aws/amazon_web_services/package/datamodel/datamodel.xml')
        assertFileExists(self, 'aws/amazon_web_services/package/Configuration/shellconfig.xml')
        assertFileExists(self, 'aws/amazon_web_services/package/Resource Drivers - Python/aws Driver.zip')
        assertFileExists(self, 'aws/amazon_web_services/dist/aws.zip')








