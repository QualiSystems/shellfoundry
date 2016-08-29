import zipfile

from mock import patch, MagicMock
from pyfakefs import fake_filesystem_unittest

from shellfoundry.utilities.shell_datamodel_merger import ShellDataModelMerger
from tests.asserts import *
from shellfoundry.utilities.package_builder import PackageBuilder


class TestPackageBuilder(fake_filesystem_unittest.TestCase):
    def setUp(self):
        self.setUpPyfakefs()

    def test_it_merges_datamodel_if_shell_config_exists(self):
        self.fs.CreateFile('work/aws/amazon_web_services/datamodel/metadata.xml', contents='')
        self.fs.CreateFile('work/aws/amazon_web_services/datamodel/shell_model.xml', contents='')

        self.fs.CreateFile('work/aws/amazon_web_services/datamodel/datamodel.xml', contents='')
        self.fs.CreateFile('work/aws/amazon_web_services/datamodel/shellconfig.xml', contents='')

        os.chdir('work')
        builder = PackageBuilder()

        with patch('shellfoundry.utilities.package_builder.ShellDataModelMerger') as MockClass:
            # Act
            instance = MockClass.return_value
            instance.merge_shell_model.return_value = 'Test'
            builder.build_package('aws/amazon_web_services', 'aws', 'AwsDriver')
            self.assertTrue(instance.merge_shell_model.called, 'merge_shell_model should be called')

        # Assert
        TestPackageBuilder.unzip('aws/amazon_web_services/dist/aws.zip', 'aws/amazon_web_services/package')
        assertFileExists(self, 'aws/amazon_web_services/package/DataModel/datamodel.xml')

        self.assert_utf_file_content('aws/amazon_web_services/package/DataModel/datamodel.xml', 'Test')

    def test_it_does_not_merge_datamodel_if_shell_config_does_not_exist(self):
        self.fs.CreateFile('work/aws/amazon_web_services/datamodel/metadata.xml', contents='')

        self.fs.CreateFile('work/aws/amazon_web_services/datamodel/datamodel.xml', contents='')
        self.fs.CreateFile('work/aws/amazon_web_services/datamodel/shellconfig.xml', contents='')

        os.chdir('work')
        builder = PackageBuilder()

        with patch('shellfoundry.utilities.package_builder.ShellDataModelMerger') as MockClass:
            # Act
            instance = MockClass.return_value
            instance.merge_shell_model.return_value = 'Test'
            builder.build_package('aws/amazon_web_services', 'aws', 'AwsDriver')
            instance.merge_shell_model.assert_not_called()

        # Assert
        TestPackageBuilder.unzip('aws/amazon_web_services/dist/aws.zip', 'aws/amazon_web_services/package')
        assertFileExists(self, 'aws/amazon_web_services/package/DataModel/datamodel.xml')

        self.assert_utf_file_content('aws/amazon_web_services/package/DataModel/datamodel.xml', '')

    def test_it_copies_image_files_in_the_datamodel_dir(self):
        self.fs.CreateFile('work/aws/amazon_web_services/datamodel/metadata.xml', contents='')
        self.fs.CreateFile('work/aws/amazon_web_services/datamodel/datamodel.xml', contents='')
        self.fs.CreateFile('work/aws/amazon_web_services/datamodel/shellconfig.xml', contents='')
        self.fs.CreateFile('work/aws/amazon_web_services/src/driver.py', contents='')

        self.fs.CreateFile('work/aws/amazon_web_services/datamodel/iamimage.png', contents='')
        self.fs.CreateFile('work/aws/amazon_web_services/datamodel/iamimage.jpg', contents='')
        self.fs.CreateFile('work/aws/amazon_web_services/datamodel/iamimage.gif', contents='')
        self.fs.CreateFile('work/aws/amazon_web_services/datamodel/iamimage.jpeg', contents='')

        os.chdir('work')
        builder = PackageBuilder()

        # Act
        builder.build_package('aws/amazon_web_services', 'aws', 'AwsDriver')

        # Assert
        TestPackageBuilder.unzip('aws/amazon_web_services/dist/aws.zip', 'aws/amazon_web_services/package')
        assertFileExists(self, 'aws/amazon_web_services/package/DataModel/iamimage.png')
        assertFileExists(self, 'aws/amazon_web_services/package/DataModel/iamimage.jpg')
        assertFileExists(self, 'aws/amazon_web_services/package/DataModel/iamimage.gif')
        assertFileExists(self, 'aws/amazon_web_services/package/DataModel/iamimage.jpeg')

    def test_it_ignores_other_nonimage_files_in_the_datamodel_dir(self):
        self.fs.CreateFile('work/aws/amazon_web_services/datamodel/metadata.xml', contents='')
        self.fs.CreateFile('work/aws/amazon_web_services/datamodel/datamodel.xml', contents='')
        self.fs.CreateFile('work/aws/amazon_web_services/datamodel/shellconfig.xml', contents='')
        self.fs.CreateFile('work/aws/amazon_web_services/src/driver.py', contents='')

        self.fs.CreateFile('work/aws/amazon_web_services/datamodel/iamimage.blah', contents='')

        os.chdir('work')
        builder = PackageBuilder()

        # Act
        builder.build_package('aws/amazon_web_services', 'aws', 'AwsDriver')

        # Assert
        assertFileDoesNotExist(self, 'aws/amazon_web_services/package/DataModel/iamimage.blah')

    def test_build_package_package_created(self):
        # Arrange
        self.fs.CreateFile('work/aws/amazon_web_services/datamodel/metadata.xml', contents='')
        self.fs.CreateFile('work/aws/amazon_web_services/datamodel/datamodel.xml', contents='')
        self.fs.CreateFile('work/aws/amazon_web_services/datamodel/shellconfig.xml', contents='')
        self.fs.CreateFile('work/aws/amazon_web_services/src/driver.py', contents='')
        os.chdir('work')
        builder = PackageBuilder()

        # Act
        builder.build_package('aws/amazon_web_services', 'aws', 'AwsDriver')

        # Assert
        assertFileExists(self, 'aws/amazon_web_services/dist/aws.zip')
        assertFileDoesNotExist(self, 'aws/amazon_web_services/package')
        TestPackageBuilder.unzip('aws/amazon_web_services/dist/aws.zip', 'aws/amazon_web_services/package')
        assertFileExists(self, 'aws/amazon_web_services/package/metadata.xml')
        assertFileExists(self, 'aws/amazon_web_services/package/DataModel/datamodel.xml')
        assertFileExists(self, 'aws/amazon_web_services/package/Configuration/shellconfig.xml')
        assertFileExists(self, 'aws/amazon_web_services/package/Resource Drivers - Python/AwsDriver.zip')

    def test_pack_succeeds_when_shellconfig_is_missing(self):
        # Arrange
        self.fs.CreateFile('work/aws/amazon_web_services/datamodel/metadata.xml', contents='')
        self.fs.CreateFile('work/aws/amazon_web_services/datamodel/datamodel.xml', contents='')
        self.fs.CreateFile('work/aws/amazon_web_services/src/driver.py', contents='')
        os.chdir('work')
        builder = PackageBuilder()

        # Act
        builder.build_package('aws/amazon_web_services', 'aws', 'AwsDriver')

        # Assert
        assertFileExists(self, 'aws/amazon_web_services/dist/aws.zip')
        TestPackageBuilder.unzip('aws/amazon_web_services/dist/aws.zip', 'aws/amazon_web_services/package')
        assertFileExists(self, 'aws/amazon_web_services/package/metadata.xml')
        assertFileExists(self, 'aws/amazon_web_services/package/DataModel/datamodel.xml')
        assertFileExists(self, 'aws/amazon_web_services/package/Resource Drivers - Python/AwsDriver.zip')

    @staticmethod
    def unzip(source_filename, dest_dir):
        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir)
        with zipfile.ZipFile(source_filename) as zf:
            zf.extractall(dest_dir)


    def assert_utf_file_content(self, path, content):
        with open(path, 'r') as f:
            text = f.read()

        self.assertEqual(text.decode("utf-8-sig"), content, msg="File was different than expected content")





