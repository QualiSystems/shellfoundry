import xml.etree.ElementTree as etree


class ShellDataModelMerger:

    def _parse_xml(self, xml_string):
        parser = etree.XMLParser(encoding='utf-8')
        return etree.fromstring(xml_string, parser)

    def merge_shell_model(self, datamodel, shell_model):
        etree.register_namespace('', "http://schemas.qualisystems.com/ResourceManagement/DataModelSchema.xsd")
        datamodel_tree = self._parse_xml(datamodel)
        shell_tree = self._parse_xml(shell_model)

        shell_family_element = shell_tree.find(".//ShellModel")
        if shell_family_element is None:
            raise Exception("Missing ShellModel element in shell_model.xml file")

        family_name = shell_family_element.get("Family")

        family_xpath_expression = ".//{{http://schemas.qualisystems.com/ResourceManagement/DataModelSchema.xsd}}ResourceFamily[@Name='{family_name}']".format(
            family_name=family_name)
        dm_family_element = datamodel_tree.find(family_xpath_expression)

        if dm_family_element is None:
            raise Exception("Shell family not found:" + family_name)
        model_insertion_point = dm_family_element.find(".//{http://schemas.qualisystems.com/ResourceManagement/DataModelSchema.xsd}Models")
        models =shell_tree.find(".//ShellModel")
        model_insertion_point.extend(models)

        attributes =shell_tree.find(".//ShellAttributes")
        attributes_insertion_point = datamodel_tree.find(".//{http://schemas.qualisystems.com/ResourceManagement/DataModelSchema.xsd}Attributes")
        attributes_insertion_point.extend(attributes)

        return etree.tostring(datamodel_tree)
