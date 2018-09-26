import os
import xml.etree.ElementTree as etree
import ast
import _ast


class DriverMetadataValidations(object):

    @staticmethod
    def _parse_xml(xml_string):
        # type: (str) -> etree.Element
        """
        :param xml_string: xml string
        :return: etree.Element xml element from the input string
        """
        parser = etree.XMLParser(encoding='utf-8')
        return etree.fromstring(xml_string, parser)

    @staticmethod
    def _get_driver_commands(driver_path, driver_name):
        """
        :param driver_path:
        :return: dict: public command names dictionary
        """
        if os.path.exists(driver_path):
            with open(driver_path) as mf:
                tree = ast.parse(mf.read())

            module_classes = []
            for i in tree.body:
                if isinstance(i, _ast.ClassDef):
                    if i.name == driver_name:
                        module_classes.append(i)

            commands = {}
            for f in module_classes[0].body:
                if isinstance(f, _ast.FunctionDef) and not f.name.startswith('_'):
                    args = f.args.args
                    if len(args) >= 2:
                        if args[0].id == 'self' and args[1].id == 'context':
                            commands[f.name] = [a.id for a in f.args.args]

            return commands
        else:
            return {}

    def validate_driver_metadata(self, driver_path):
        """ Validate driver metadata
            :param str driver_path: path to the driver directory
        """

        metadata_path = os.path.join(driver_path, 'drivermetadata.xml')
        driver_path = os.path.join(driver_path, 'driver.py')
        if os.path.exists(metadata_path):
            with open(metadata_path, 'r') as f:
                metadata_str = f.read()

            metadata_xml = self._parse_xml(metadata_str)
            metadata_commands = metadata_xml.findall('.//Command')

            driver_commands = self._get_driver_commands(driver_path, 'NutShellDriver')

            missing = []
            for mc in metadata_commands:
                if mc.attrib['Name'] in driver_commands:
                    continue
                else:
                    missing.append(mc.attrib['Name'])

            if len(missing) > 0:
                err = 'The following commands do not exist in the driver.py but still mentioned in ' \
                      'the DriverMetadata.xml file: {}.\nPlease update the metadata or driver files accordingly.'.format(', '.join(missing))
                raise Exception(err)

            # TODO: add validation for command inputs as well
