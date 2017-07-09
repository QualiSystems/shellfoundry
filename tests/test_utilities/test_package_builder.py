import zipfile

from mock import patch, Mock
from pyfakefs import fake_filesystem_unittest

from tests.asserts import *
from shellfoundry.utilities.package_builder import PackageBuilder
import xml.etree.ElementTree as etree


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
            with patch('click.echo'):
                builder.build_package('aws/amazon_web_services', 'aws', 'AwsDriver')
            self.assertTrue(instance.merge_shell_model.called, 'merge_shell_model should be called')

        # Assert
        TestPackageBuilder.unzip('aws/amazon_web_services/dist/aws.zip', 'aws/amazon_web_services/package')
        assertFileExists(self, 'aws/amazon_web_services/package/DataModel/datamodel.xml')

        self._assert_utf_file_content('aws/amazon_web_services/package/DataModel/datamodel.xml', 'Test')

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
            with patch('click.echo'):
                builder.build_package('aws/amazon_web_services', 'aws', 'AwsDriver')
            instance.merge_shell_model.assert_not_called()

        # Assert
        TestPackageBuilder.unzip('aws/amazon_web_services/dist/aws.zip', 'aws/amazon_web_services/package')
        assertFileExists(self, 'aws/amazon_web_services/package/DataModel/datamodel.xml')

        self._assert_utf_file_content('aws/amazon_web_services/package/DataModel/datamodel.xml', '')

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
        with patch('click.echo'):
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
        with patch('click.echo'):
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
        with patch('click.echo'):
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
        with patch('click.echo'):
            builder.build_package('aws/amazon_web_services', 'aws', 'AwsDriver')

        # Assert
        assertFileExists(self, 'aws/amazon_web_services/dist/aws.zip')
        TestPackageBuilder.unzip('aws/amazon_web_services/dist/aws.zip', 'aws/amazon_web_services/package')
        assertFileExists(self, 'aws/amazon_web_services/package/metadata.xml')
        assertFileExists(self, 'aws/amazon_web_services/package/DataModel/datamodel.xml')
        assertFileExists(self, 'aws/amazon_web_services/package/Resource Drivers - Python/AwsDriver.zip')

    def test_pack_succeeds_when_categories_file_is_missing(self):
        # Arrange
        self.fs.CreateFile('work/aws/amazon_web_services/datamodel/metadata.xml', contents='')
        self.fs.CreateFile('work/aws/amazon_web_services/datamodel/datamodel.xml', contents='')
        self.fs.CreateFile('work/aws/amazon_web_services/src/driver.py', contents='')
        os.chdir('work')
        builder = PackageBuilder()

        # Act
        with patch('click.echo'):
            builder.build_package('aws/amazon_web_services', 'aws', 'AwsDriver')

        # Assert
        assertFileExists(self, 'aws/amazon_web_services/dist/aws.zip')
        TestPackageBuilder.unzip('aws/amazon_web_services/dist/aws.zip', 'aws/amazon_web_services/package')
        assertFileExists(self, 'aws/amazon_web_services/package/metadata.xml')
        assertFileExists(self, 'aws/amazon_web_services/package/DataModel/datamodel.xml')
        assertFileExists(self, 'aws/amazon_web_services/package/Resource Drivers - Python/AwsDriver.zip')

    def test_pack_succeeds_when_categories_file_exists(self):
        # Arrange
        self.fs.CreateFile('work/aws/amazon_web_services/datamodel/metadata.xml', contents='')
        self.fs.CreateFile('work/aws/amazon_web_services/datamodel/datamodel.xml', contents='')
        self.fs.CreateFile('work/aws/amazon_web_services/categories/categories.xml', contents='')
        self.fs.CreateFile('work/aws/amazon_web_services/src/driver.py', contents='')
        os.chdir('work')
        builder = PackageBuilder()

        # Act
        with patch('click.echo'):
            builder.build_package('aws/amazon_web_services', 'aws', 'AwsDriver')

        # Assert
        assertFileExists(self, 'aws/amazon_web_services/dist/aws.zip')
        TestPackageBuilder.unzip('aws/amazon_web_services/dist/aws.zip', 'aws/amazon_web_services/package')
        assertFileExists(self, 'aws/amazon_web_services/package/metadata.xml')
        assertFileExists(self, 'aws/amazon_web_services/package/DataModel/datamodel.xml')
        assertFileExists(self, 'aws/amazon_web_services/package/Categories/categories.xml')
        assertFileExists(self, 'aws/amazon_web_services/package/Resource Drivers - Python/AwsDriver.zip')

    def test_it_replaces_wildcard_according_to_versioning_policy(self):
        self.fs.CreateFile('work/aws/amazon_web_services/datamodel/metadata.xml', contents='')
        self.fs.CreateFile('work/aws/amazon_web_services/datamodel/datamodel.xml', contents='')
        self.fs.CreateFile('work/aws/amazon_web_services/datamodel/shellconfig.xml', contents='')
        self.fs.CreateFile('work/aws/amazon_web_services/src/driver.py', contents='')
        self.fs.CreateFile('work/aws/amazon_web_services/src/drivermetadata.xml',
                           contents='<Driver Description="CloudShell shell" '
                                    'MainClass="driver.ImplementingDiscoveryDriver" '
                                    'Name="ImplementingDiscoveryDriver" Version="1.2.*">'
                                    '</Driver>')

        os.chdir('work')
        driver_version_strategy = Mock()
        driver_version_strategy.supports_version_pattern.return_value = True
        driver_version_strategy.get_version.return_value = '1.2.3.4'
        builder = PackageBuilder(driver_version_strategy)

        # Act
        with patch('click.echo'):
            builder.build_package('aws/amazon_web_services', 'aws', 'AwsDriver')

        # Assert
        TestPackageBuilder.unzip('aws/amazon_web_services/dist/aws.zip', 'aws/amazon_web_services/package')
        assertFileExists(self, 'aws/amazon_web_services/package/Resource Drivers - Python/AwsDriver.zip')
        TestPackageBuilder.unzip('aws/amazon_web_services/package/Resource Drivers - Python/AwsDriver.zip',
                                 'aws/driver')
        assertFileExists(self, 'aws/driver/drivermetadata.xml')

        # packed file should have a dynamic version
        self._assert_driver_version_equals('aws/driver/drivermetadata.xml', '1.2.3.4')
        # original file should still have the original value
        self._assert_driver_version_equals('aws/amazon_web_services/src/drivermetadata.xml', '1.2.*')

    def test_it_uses_the_datetime_stamp_policy_for_wildcard_versioning(self):
        self.fs.CreateFile('work/aws/amazon_web_services/datamodel/metadata.xml', contents='')
        self.fs.CreateFile('work/aws/amazon_web_services/datamodel/datamodel.xml', contents='')
        self.fs.CreateFile('work/aws/amazon_web_services/datamodel/shellconfig.xml', contents='')
        self.fs.CreateFile('work/aws/amazon_web_services/src/driver.py', contents='')
        self.fs.CreateFile('work/aws/amazon_web_services/src/drivermetadata.xml',
                           contents='<Driver Description="CloudShell shell" '
                                    'MainClass="driver.ImplementingDiscoveryDriver" '
                                    'Name="ImplementingDiscoveryDriver" Version="1.2.*">'
                                    '</Driver>')

        os.chdir('work')

        # Act
        with patch('shellfoundry.utilities.package_builder.DriverVersionTimestampBased') as version_mock:
            strategy_instance = Mock()
            version_mock.return_value = strategy_instance
            strategy_instance.get_version.return_value = '1.2.3000.4000'
            builder = PackageBuilder()
            with patch('click.echo'):
                builder.build_package('aws/amazon_web_services', 'aws', 'AwsDriver')

        # Assert
        TestPackageBuilder.unzip('aws/amazon_web_services/dist/aws.zip', 'aws/amazon_web_services/package')
        assertFileExists(self, 'aws/amazon_web_services/package/Resource Drivers - Python/AwsDriver.zip')
        TestPackageBuilder.unzip('aws/amazon_web_services/package/Resource Drivers - Python/AwsDriver.zip',
                                 'aws/driver')
        assertFileExists(self, 'aws/driver/drivermetadata.xml')

        # packed file should have a dynamic version
        self._assert_driver_version_equals('aws/driver/drivermetadata.xml', '1.2.3000.4000')
        # original file should still have the original value
        self._assert_driver_version_equals('aws/amazon_web_services/src/drivermetadata.xml', '1.2.*')

    def test_it_does_not_update_the_driver_version_when_not_needed(self):
        self.fs.CreateFile('work/aws/amazon_web_services/datamodel/metadata.xml', contents='')
        self.fs.CreateFile('work/aws/amazon_web_services/datamodel/datamodel.xml', contents='')
        self.fs.CreateFile('work/aws/amazon_web_services/datamodel/shellconfig.xml', contents='')
        self.fs.CreateFile('work/aws/amazon_web_services/src/driver.py', contents='')
        self.fs.CreateFile('work/aws/amazon_web_services/src/drivermetadata.xml',
                           contents='<Driver Description="CloudShell shell" '
                                    'MainClass="driver.ImplementingDiscoveryDriver" '
                                    'Name="ImplementingDiscoveryDriver" Version="1.2.3">'
                                    '</Driver>')

        os.chdir('work')
        builder = PackageBuilder()

        # Act
        with patch('click.echo'):
            builder.build_package('aws/amazon_web_services', 'aws', 'AwsDriver')

        # Assert
        TestPackageBuilder.unzip('aws/amazon_web_services/dist/aws.zip', 'aws/amazon_web_services/package')
        assertFileExists(self, 'aws/amazon_web_services/package/Resource Drivers - Python/AwsDriver.zip')
        TestPackageBuilder.unzip('aws/amazon_web_services/package/Resource Drivers - Python/AwsDriver.zip',
                                 'aws/driver')
        assertFileExists(self, 'aws/driver/drivermetadata.xml')

        # packed file should not have a timestamped version
        self._assert_driver_version_equals('aws/driver/drivermetadata.xml', '1.2.3')
        # original file should still have the original value
        self._assert_driver_version_equals('aws/amazon_web_services/src/drivermetadata.xml', '1.2.3')

    @staticmethod
    def unzip(source_filename, dest_dir):
        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir)
        with zipfile.ZipFile(source_filename) as zf:
            zf.extractall(dest_dir)

    @staticmethod
    def _parse_xml(xml_string):
        parser = etree.XMLParser(encoding='utf-8')
        return etree.fromstring(xml_string, parser)

    def _assert_utf_file_content(self, path, content):
        with open(path, 'r') as f:
            text = f.read()

        self.assertEqual(text.decode("utf-8-sig"), content, msg="File was different than expected content")

    @staticmethod
    def _get_driver_version_from_file(path):
        with open(path, 'r') as f:
            text = f.read()

        metadata_xml = TestPackageBuilder._parse_xml(text)
        version = metadata_xml.get("Version")
        return version

    def _assert_driver_version_equals(self, path, expected_version):
        version = self._get_driver_version_from_file(path)
        self.assertEquals(version, expected_version)
