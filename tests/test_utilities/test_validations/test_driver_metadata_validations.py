from mock import patch
from pyfakefs import fake_filesystem_unittest
from tests.asserts import *

from shellfoundry.utilities.validations import DriverMetadataValidations

drivermetadataxml = """
            <Driver Description="shell description" MainClass="driver.NutShellDriver" Name="NutShellDriver" Version="1.0.0">
        <Layout>
             <Category Name="Hidden Commands">
                <Command Description="" DisplayName="Orchestration Save" Name="orchestration_save" />
                <Command Description="" DisplayName="Orchestration Restore" Name="orchestration_restore" />
            </Category>
        </Layout>
    </Driver>
                """


class TestDriverMetadataValidations(fake_filesystem_unittest.TestCase):
    def setUp(self):
        self.setUpPyfakefs()

    def test_not_failing_when_more_commands_in_driver_than_in_metadata(self):
        # Arrange
        self.fs.CreateFile('nut_shell/src/drivermetadata.xml', contents=drivermetadataxml)
        self.fs.CreateFile('nut_shell/src/requirements.txt')
        self.fs.CreateFile('nut_shell/src/driver.py', contents="""
from cloudshell.shell.core.resource_driver_interface import ResourceDriverInterface
from cloudshell.shell.core.driver_context import InitCommandContext, ResourceCommandContext, AutoLoadResource, \
    AutoLoadAttribute, AutoLoadDetails, CancellationContext

class NutShellDriver (ResourceDriverInterface):

    def __init__(self):
        pass

    def initialize(self, context):
        pass
    
    def _internal_function(self, context):
        pass
    
    @staticmethod
    def mystatic():
        pass

    def cleanup(self):
        pass

    # <editor-fold desc="Discovery">

    def get_inventory(self, context):
        return AutoLoadDetails([], [])

    # </editor-fold>

    # <editor-fold desc="Orchestration Save and Restore Standard">
    def orchestration_save(self, context, cancellation_context, mode, custom_params):
        pass

    def orchestration_restore(self, context, cancellation_context, saved_artifact_info, custom_params):
        pass

    # </editor-fold>
            """)
        # os.chdir('nut_shell')

        driver_path = 'nut_shell/src'
        validations = DriverMetadataValidations()

        # Act
        try:
            validations.validate_driver_metadata(driver_path)
        except Exception as ex:
            self.fail('validate_driver_metadata raised an exception when it shouldn\'t: ' + ex.message)

    def test_fails_when_command_in_metadata_but_not_in_driver(self):
        # Arrange
        self.fs.CreateFile('nut_shell/src/drivermetadata.xml', contents=drivermetadataxml)
        self.fs.CreateFile('nut_shell/src/requirements.txt')
        self.fs.CreateFile('nut_shell/src/driver.py', contents="""
from cloudshell.shell.core.resource_driver_interface import ResourceDriverInterface
from cloudshell.shell.core.driver_context import InitCommandContext, ResourceCommandContext, AutoLoadResource, \
    AutoLoadAttribute, AutoLoadDetails, CancellationContext

class NutShellDriver (ResourceDriverInterface):

    def __init__(self):
        pass

    def orchestration_save(self, context, cancellation_context, mode, custom_params):
        pass

            """)
        # os.chdir('nut_shell')

        driver_path = 'nut_shell/src'
        validations = DriverMetadataValidations()

        # Act
        with self.assertRaises(Exception) as context:
            validations.validate_driver_metadata(driver_path)

        # Assert
        self.assertEqual(context.exception.message, """The following commands do not exist in the driver.py but still mentioned in the DriverMetadata.xml file: orchestration_restore.
Please update the metadata or driver files accordingly.""")

