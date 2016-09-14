import codecs
import os
import unittest
import mock
import xml.etree.ElementTree as etree

from shellfoundry.utilities.shell_datamodel_merger import ShellDataModelMerger


class TestDataModelMerger(unittest.TestCase):

    # def test_works_with_utf_files(self):
    #
    #     with codecs.open(os.path.join(".","test_data","datamodel.xml"), 'r', encoding='utf8') as f:
    #         dm = f.read()
    #
    #     with codecs.open(os.path.join(".","test_data","shell_model.xml"), 'r', encoding='utf8') as f:
    #         shell = f.read()
    #
    #     merger = ShellDataModelMerger()
    #     merged_xml = merger.merge_shell_model(dm, shell)
    #     self.assertIsNotNone(merged_xml)

    def test_merges_attributes(self):

        datamodel = """<?xml version="1.0" encoding="utf-8"?>
            <DataModelInfo xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://schemas.qualisystems.com/ResourceManagement/DataModelSchema.xsd">
              <Attributes>
              </Attributes>
              <ResourceFamilies>
                <ResourceFamily Name="Switch" Description="" IsSearchable="true" IsPowerSwitch="true">
                  <AttachedAttributes />
                  <AttributeValues />
                  <Models>
                  </Models>
                  <Categories />
                </ResourceFamily>

              </ResourceFamilies>
              <DriverDescriptors />
              <ScriptDescriptors />
            </DataModelInfo>
        """

        shell = """
            <Shell>
            <ShellAttributes>
             <AttributeInfo Name="Shell Enable Password" Type="Password" DefaultValue="3M3u7nkDzxWb0aJ/IZYeWw==" IsReadOnly="false">
                <Rules>
                 <Rule Name="Configuration" />
                </Rules>
                 </AttributeInfo>
                <AttributeInfo Name="Shell Power Management" Type="Boolean" DefaultValue="False" IsReadOnly="false">
              <Rules>
                 <Rule Name="Configuration" />
              </Rules>
               </AttributeInfo>
            </ShellAttributes>

            <ShellModel Family="Switch">
                <ResourceModel Name="SSwitch" Description="" SupportsConcurrentCommands="true">
                    <AttachedAttributes>
                    </AttachedAttributes>
                    <AttributeValues>
                    </AttributeValues>
                    <Drivers>
                        <DriverName>SSwitchDriver</DriverName>
                    </Drivers>
                    <Scripts />
                </ResourceModel>
            </ShellModel>
            </Shell>
        """
        merger = ShellDataModelMerger()
        merged_xml = merger.merge_shell_model(datamodel, shell)

        parser = etree.XMLParser(encoding='utf-8')
        tree = etree.fromstring(merged_xml, parser)

        self.assertIsNotNone(tree.find(".//{http://schemas.qualisystems.com/ResourceManagement/DataModelSchema.xsd}AttributeInfo[@Name='Shell Enable Password']"),
                             "Attribute was not found in merged xml")

        self.assertIsNotNone(tree.find(
            ".//{http://schemas.qualisystems.com/ResourceManagement/DataModelSchema.xsd}AttributeInfo[@Name='Shell Power Management']"),
                             "Attribute was not found in merged xml"
        )

    def test_exception_thrown_when_family_missing_in_data_model(self):

        datamodel = """<?xml version="1.0" encoding="utf-8"?>
            <DataModelInfo xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://schemas.qualisystems.com/ResourceManagement/DataModelSchema.xsd">
              <Attributes>
              </Attributes>
              <ResourceFamilies>
                <ResourceFamily Name="Switch" Description="" IsSearchable="true" IsPowerSwitch="true">
                  <AttachedAttributes />
                  <AttributeValues />
                  <Models>
                  </Models>
                  <Categories />
                </ResourceFamily>

              </ResourceFamilies>
              <DriverDescriptors />
              <ScriptDescriptors />
            </DataModelInfo>
        """

        shell = """
            <Shell>
            <ShellAttributes>
             <AttributeInfo Name="Shell Enable Password" Type="Password" DefaultValue="3M3u7nkDzxWb0aJ/IZYeWw==" IsReadOnly="false">
                <Rules>
                 <Rule Name="Configuration" />
                </Rules>
                 </AttributeInfo>
                <AttributeInfo Name="Shell Power Management" Type="Boolean" DefaultValue="False" IsReadOnly="false">
              <Rules>
                 <Rule Name="Configuration" />
              </Rules>
               </AttributeInfo>
            </ShellAttributes>

            <ShellModel Family="NON EXISTING FAMILY">
                <ResourceModel Name="SSwitch" Description="" SupportsConcurrentCommands="true">
                    <AttachedAttributes>
                    </AttachedAttributes>
                    <AttributeValues>
                    </AttributeValues>
                    <Drivers>
                        <DriverName>SSwitchDriver</DriverName>
                    </Drivers>
                    <Scripts />
                </ResourceModel>
            </ShellModel>
            </Shell>
        """
        merger = ShellDataModelMerger()

        # Assert
        self.assertRaises(Exception, merger.merge_shell_model, datamodel, shell)

    def test_exception_thrown_when_shell_model_missing_in_data_model(self):

        datamodel = """<?xml version="1.0" encoding="utf-8"?>
            <DataModelInfo xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://schemas.qualisystems.com/ResourceManagement/DataModelSchema.xsd">
              <Attributes>
              </Attributes>
              <ResourceFamilies>
                <ResourceFamily Name="Switch" Description="" IsSearchable="true" IsPowerSwitch="true">
                  <AttachedAttributes />
                  <AttributeValues />
                  <Models>
                  </Models>
                  <Categories />
                </ResourceFamily>
              </ResourceFamilies>
              <DriverDescriptors />
              <ScriptDescriptors />
            </DataModelInfo>
        """

        shell = """
            <Shell>
            <ShellAttributes>
             <AttributeInfo Name="Shell Enable Password" Type="Password" DefaultValue="3M3u7nkDzxWb0aJ/IZYeWw==" IsReadOnly="false">
                <Rules>
                 <Rule Name="Configuration" />
                </Rules>
                 </AttributeInfo>
                <AttributeInfo Name="Shell Power Management" Type="Boolean" DefaultValue="False" IsReadOnly="false">
              <Rules>
                 <Rule Name="Configuration" />
              </Rules>
               </AttributeInfo>
            </ShellAttributes>
            </Shell>
        """
        merger = ShellDataModelMerger()

        # Assert
        self.assertRaises(Exception, merger.merge_shell_model, datamodel, shell)

    def test_adds_the_shell_model_to_the_datamodel(self):

        datamodel = """<?xml version="1.0" encoding="utf-8"?>
            <DataModelInfo xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://schemas.qualisystems.com/ResourceManagement/DataModelSchema.xsd">
              <Attributes>
              </Attributes>
              <ResourceFamilies>
                <ResourceFamily Name="Switch" Description="" IsSearchable="true" IsPowerSwitch="true">
                  <AttachedAttributes />
                  <AttributeValues />
                  <Models>
                  </Models>
                  <Categories />
                </ResourceFamily>

              </ResourceFamilies>
              <DriverDescriptors />
              <ScriptDescriptors />
            </DataModelInfo>
        """

        shell = """
            <Shell>

            <ShellAttributes>
            </ShellAttributes>

            <ShellModel Family="Switch">
                <ResourceModel Name="SSwitch" Description="" SupportsConcurrentCommands="true">
                    <AttachedAttributes>
                    </AttachedAttributes>
                    <AttributeValues>
                    </AttributeValues>
                    <Drivers>
                        <DriverName>SSwitchDriver</DriverName>
                    </Drivers>
                    <Scripts />
                </ResourceModel>
            </ShellModel>
            </Shell>
        """

        merger = ShellDataModelMerger()
        merged_xml = merger.merge_shell_model(datamodel, shell)

        parser = etree.XMLParser(encoding='utf-8')
        tree = etree.fromstring(merged_xml, parser)

        self.assertIsNotNone(tree.find(".//{http://schemas.qualisystems.com/ResourceManagement/DataModelSchema.xsd}ResourceModel"),
                             "Model was not found in merged xml")

    def test_addds_the_shell_model_to_the_target_family(self):
        datamodel = """<?xml version="1.0" encoding="utf-8"?>
              <DataModelInfo xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://schemas.qualisystems.com/ResourceManagement/DataModelSchema.xsd">
                <Attributes>
                </Attributes>
                <ResourceFamilies>
                  <ResourceFamily Name="Bait" Description="" IsSearchable="true" IsPowerSwitch="true">
                    <AttachedAttributes />
                    <AttributeValues />
                    <Models>
                    </Models>
                    <Categories />
                  </ResourceFamily>
                  <ResourceFamily Name="Switch" Description="" IsSearchable="true" IsPowerSwitch="true">
                    <AttachedAttributes />
                    <AttributeValues />
                    <Models>
                    </Models>
                    <Categories />
                  </ResourceFamily>
                </ResourceFamilies>
                <DriverDescriptors />
                <ScriptDescriptors />
              </DataModelInfo>
          """

        shell = """
              <Shell>

              <ShellAttributes>
              </ShellAttributes>

              <ShellModel Family="Switch">
                  <ResourceModel Name="SSwitch" Description="" SupportsConcurrentCommands="true">
                      <AttachedAttributes>
                      </AttachedAttributes>
                      <AttributeValues>
                      </AttributeValues>
                      <Drivers>
                          <DriverName>SSwitchDriver</DriverName>
                      </Drivers>
                      <Scripts />
                  </ResourceModel>
              </ShellModel>
              </Shell>
          """

        merger = ShellDataModelMerger()
        merged_xml = merger.merge_shell_model(datamodel, shell)

        parser = etree.XMLParser(encoding='utf-8')
        tree = etree.fromstring(merged_xml, parser)

        family = tree.find(".//{http://schemas.qualisystems.com/ResourceManagement/DataModelSchema.xsd}ResourceFamily[@Name='Switch']")

        self.assertIsNotNone(
            family.find(".//{http://schemas.qualisystems.com/ResourceManagement/DataModelSchema.xsd}ResourceModel[@Name='SSwitch']"),
        "Model was not found in merged xml")

        bait_family = tree.find(
            ".//{http://schemas.qualisystems.com/ResourceManagement/DataModelSchema.xsd}ResourceFamily[@Name='Bait']")

        self.assertIsNone(
            bait_family.find(
                ".//{http://schemas.qualisystems.com/ResourceManagement/DataModelSchema.xsd}ResourceModel[@Name='SSwitch']"),
            "Model was added to wrong element")
