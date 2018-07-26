#!/usr/bin/python
# -*- coding: utf-8 -*-

import unittest
import httpretty

from pyfakefs import fake_filesystem_unittest

from click import UsageError, ClickException
from mock import Mock, MagicMock, patch
from requests.exceptions import SSLError
from cloudshell.rest.api import FeatureUnavailable
from shellfoundry.commands.list_command import ListCommandExecutor
from shellfoundry.models.shell_template import ShellTemplate
from shellfoundry.utilities.template_retriever import FilteredTemplateRetriever, TemplateRetriever, TEMPLATES_YML


class TestListCommand(unittest.TestCase):
    @patch('click.echo')
    @patch('shellfoundry.commands.list_command.AsciiTable.column_max_width')
    def test_single_template_is_displayed(self, max_width_mock, echo_mock):
        # Arrange
        max_width_mock.return_value = 62  # mocking the max width to eliminate the distinction
        # between the running console size

        template_retriever = Mock()
        template_retriever.get_templates = Mock(
            return_value={'gen1/base': [ShellTemplate('gen1/base', 'description', '', '7.0')]})

        standards = Mock()
        standards.fetch.return_value = {}

        list_command_executor = ListCommandExecutor(template_retriever=template_retriever, standards=standards)

        # Act
        list_command_executor.list()

        # Assert
        echo_mock.assert_any_call(u' Template Name  CloudShell Ver.  Description \n'
                                  u'---------------------------------------------\n'
                                  u' gen1/base      7.0 and up       description ')

    @patch('shellfoundry.commands.list_command.Configuration')
    def test_shows_informative_message_when_offline(self, conf_class):
        # Arrange
        configuration = MagicMock(read=MagicMock(return_value=MagicMock(online_mode="True")))
        conf_class.return_value = configuration
        template_retriever = Mock()
        template_retriever.get_templates.side_effect = SSLError()
        list_command_executor = ListCommandExecutor(template_retriever=template_retriever,
                                                    standards=Mock())

        # Assert
        self.assertRaisesRegexp(UsageError, "offline", list_command_executor.list)

    @patch('click.echo')
    @patch('shellfoundry.commands.list_command.AsciiTable.column_max_width')
    def test_two_templates_are_displayed(self, max_width_mock, echo_mock):
        # Arrange
        max_width_mock.return_value = 62  # mocking the max width to eliminate the distinction
        # between the running console size

        template_retriever = Mock()
        template_retriever.get_templates = Mock(return_value={
            'gen1/base': [ShellTemplate('gen1/base', 'base description', '', '7.0', 'base')],
            'gen1/switch': [ShellTemplate('gen1/switch', 'switch description', '', '7.0')]})

        standards = Mock()
        standards.fetch.return_value = {}

        list_command_executor = ListCommandExecutor(template_retriever=template_retriever, standards=standards)

        # Act
        list_command_executor.list()

        # Assert
        echo_mock.assert_any_call(
            u' Template Name  CloudShell Ver.  Description        \n'
            u'----------------------------------------------------\n'
            u' gen1/base      7.0 and up       base description   \n'
            u' gen1/switch    7.0 and up       switch description ')

    @patch('click.echo')
    @patch('shellfoundry.commands.list_command.AsciiTable.column_max_width')
    def test_two_long_named_templates_are_displayed_on_normal_window(self, max_width_mock, echo_mock):
        # Arrange
        max_width_mock.return_value = 40  # mocking the max width to eliminate the distinction
        # between the running console size

        template_retriever = Mock()
        template_retriever.get_templates = Mock(return_value={
            'gen2/networking/switch': [ShellTemplate('gen2/networking/switch',
                                                     'TOSCA based template for standard Switch devices/virtual appliances',
                                                     '', '8.0')],
            'gen2/networking/WirelessController': [ShellTemplate('gen2/networking/WirelessController',
                                                                 'TOSCA based template for standard WirelessController devices/virtual appliances',
                                                                 '', '8.0')]})

        standards = Mock()
        standards.fetch.return_value = {}

        list_command_executor = ListCommandExecutor(template_retriever=template_retriever, standards=standards)

        # Act
        list_command_executor.list()

        # Assert
        echo_mock.assert_any_call(
            u' Template Name                       CloudShell Ver.  Description                              \n'
            u'-----------------------------------------------------------------------------------------------\n'
            u' gen2/networking/WirelessController  8.0 and up       TOSCA based template for standard        \n'
            u'                                                      WirelessController devices/virtual       \n'
            u'                                                      appliances                               \n'
            u' gen2/networking/switch              8.0 and up       TOSCA based template for standard Switch \n'
            u'                                                      devices/virtual appliances               '
        )

    @patch('click.echo')
    @patch('shellfoundry.commands.list_command.AsciiTable.column_max_width')
    def test_console_size_small_description_wrapping_logic_ignored(self, max_width_mock, echo_mock):
        # Arrange
        max_width_mock.return_value = 0
        template_retriever = Mock()
        template_retriever.get_templates = Mock(return_value={
            'gen2/networking/switch': [ShellTemplate('gen2/networking/switch',
                                                     'TOSCA based template for standard Switch devices/virtual appliances',
                                                     '', '8.0')],
            'gen2/networking/WirelessController': [ShellTemplate('gen2/networking/WirelessController',
                                                                 'TOSCA based template for standard WirelessController devices/virtual appliances',
                                                                 '', '8.0')]})

        standards = Mock()
        standards.fetch.return_value = {"networking": ['2.0.0'],
                                        "resource": ['5.0.0', '5.0.1'],
                                        "vido": ['3.0.1', '3.0.2', '3.0.3']}
        list_command_executor = ListCommandExecutor(template_retriever=template_retriever, standards=standards)

        # Act
        list_command_executor.list()

        # Assert
        echo_mock.assert_called_once_with(
            u' Template Name                       CloudShell Ver.  Description                                                                     \n'
            u'--------------------------------------------------------------------------------------------------------------------------------------\n'
            u' gen2/networking/WirelessController  8.0 and up       TOSCA based template for standard WirelessController devices/virtual appliances \n'
            u' gen2/networking/switch              8.0 and up       TOSCA based template for standard Switch devices/virtual appliances             '
        )

    @patch('click.echo')
    @patch('shellfoundry.commands.list_command.AsciiTable.column_max_width')
    def test_filter_by_tosca_shows_all_tosca_templates(self, max_width_mock, echo_mock):
        # Arrange
        max_width_mock.return_value = 40
        template_retriever = Mock()
        template_retriever.get_templates = Mock(return_value={
            'gen2/networking/switch': [ShellTemplate('gen2/networking/switch',
                                                     'TOSCA based template for standard Switch devices/virtual appliances',
                                                     '', '8.0')],
            'gen2/networking/WirelessController': [ShellTemplate('gen2/networking/WirelessController',
                                                                 'TOSCA based template for standard WirelessController devices/virtual appliances',
                                                                 '', '8.0')],
            'gen1/base': [ShellTemplate('gen1/base', 'base description', '', '7.0')],
            'gen1/switch': [ShellTemplate('gen1/switch', 'switch description', '', '7.0')]})
        flag_value = 'gen2'

        standards = Mock()
        standards.fetch.return_value = {}

        list_command_executor = ListCommandExecutor(
            template_retriever=FilteredTemplateRetriever(flag_value, template_retriever), standards=standards)

        # Act
        list_command_executor.list()

        # Assert
        echo_mock.assert_any_call(
            u' Template Name                       CloudShell Ver.  Description                              \n'
            u'-----------------------------------------------------------------------------------------------\n'
            u' gen2/networking/WirelessController  8.0 and up       TOSCA based template for standard        \n'
            u'                                                      WirelessController devices/virtual       \n'
            u'                                                      appliances                               \n'
            u' gen2/networking/switch              8.0 and up       TOSCA based template for standard Switch \n'
            u'                                                      devices/virtual appliances               ')

    @patch('click.echo')
    @patch('shellfoundry.commands.list_command.AsciiTable.column_max_width')
    def test_filter_by_legacy_shows_all_legacy_templates(self, max_width_mock, echo_mock):
        # Arrange
        max_width_mock.return_value = 62
        template_retriever = Mock()
        template_retriever.get_templates = Mock(return_value={
            'gen2/networking/switch': [ShellTemplate('gen2/networking/switch',
                                                     'TOSCA based template for standard Switch devices/virtual appliances',
                                                     '', '8.0')],
            'gen2/networking/WirelessController': [ShellTemplate('gen2/networking/WirelessController',
                                                                 'TOSCA based template for standard WirelessController devices/virtual appliances',
                                                                 '', '8.0')],
            'gen1/base': [ShellTemplate('gen1/base', 'base description', '', '7.0')],
            'gen1/switch': [ShellTemplate('gen1/switch', 'switch description', '', '7.0')]})
        flag_value = 'gen1'

        standards = Mock()
        standards.fetch.return_value = {}

        list_command_executor = ListCommandExecutor(
            template_retriever=FilteredTemplateRetriever(flag_value, template_retriever), standards=standards)

        # Act
        list_command_executor.list()

        # Assert
        echo_mock.assert_any_call(
            u' Template Name  CloudShell Ver.  Description        \n'
            u'----------------------------------------------------\n'
            u' gen1/base      7.0 and up       base description   \n'
            u' gen1/switch    7.0 and up       switch description ')

    @patch('click.echo')
    @patch('shellfoundry.commands.list_command.AsciiTable.column_max_width')
    def test_filter_by_all_shows_all_templates(self, max_width_mock, echo_mock):
        # Arrange
        max_width_mock.return_value = 40
        template_retriever = Mock()
        template_retriever.get_templates = Mock(return_value={
            'gen1/base': [ShellTemplate('gen1/base', 'base description', '', '7.0')],
            'gen1/switch': [ShellTemplate('gen1/switch', 'switch description', '', '7.0')],
            'gen2/networking/switch': [ShellTemplate('gen2/networking/switch',
                                                     'TOSCA based template for standard Switch devices/virtual appliances',
                                                     '', '8.0')],
            'gen2/networking/WirelessController': [ShellTemplate('gen2/networking/WirelessController',
                                                                 'TOSCA based template for standard WirelessController devices/virtual appliances',
                                                                 '', '8.0')]})
        flag_value = 'all'

        standards = Mock()
        standards.fetch.return_value = {}

        list_command_executor = ListCommandExecutor(
            template_retriever=FilteredTemplateRetriever(flag_value, template_retriever), standards=standards)

        # Act
        list_command_executor.list()

        # Assert
        echo_mock.assert_any_call(
            u' Template Name                       CloudShell Ver.  Description                              \n'
            u'-----------------------------------------------------------------------------------------------\n'
            u' gen2/networking/WirelessController  8.0 and up       TOSCA based template for standard        \n'
            u'                                                      WirelessController devices/virtual       \n'
            u'                                                      appliances                               \n'
            u' gen1/base                           7.0 and up       base description                         \n'
            u' gen1/switch                         7.0 and up       switch description                       \n'
            u' gen2/networking/switch              8.0 and up       TOSCA based template for standard Switch \n'
            u'                                                      devices/virtual appliances               ')

    # @patch('click.echo')
    @patch('shellfoundry.commands.list_command.AsciiTable.column_max_width')
    def test_list_shows_nothing_because_filter_is_set_for_templates_that_do_not_exist(self, max_width_mock):
        # Arrange
        max_width_mock.return_value = 40
        template_retriever = Mock()
        template_retriever.get_templates = Mock(return_value={
            'gen2/networking/switch': [ShellTemplate('gen2/networking/switch',
                                                     'TOSCA based template for standard Switch devices/virtual appliances',
                                                     '', '8.0')],
            'gen2/networking/WirelessController': [ShellTemplate('gen2/networking/WirelessController',
                                                                 'TOSCA based template for standard WirelessController devices/virtual appliances',
                                                                 '', '8.0')]})
        flag_value = 'gen1'

        standards = Mock()
        standards.fetch.return_value = {}

        list_command_executor = ListCommandExecutor(
            template_retriever=FilteredTemplateRetriever(flag_value, template_retriever), standards=standards)

        # Act
        with self.assertRaisesRegexp(ClickException, "No templates matched the criteria"):
            list_command_executor.list()

            # Assert
            # echo_mock.assert_called_once_with("No templates matched the criteria")

    @patch('click.echo')
    @patch('shellfoundry.commands.list_command.AsciiTable.column_max_width')
    def test_devguide_text_note_appears_when_no_filter_was_selected(self, max_width_mock, echo_mock):
        # Arrange
        max_width_mock.return_value = 40
        template_retriever = Mock()
        template_retriever.get_templates = Mock(return_value={
            'gen2/networking/switch': [ShellTemplate('gen2/networking/switch',
                                                     'TOSCA based template for standard Switch devices/virtual appliances',
                                                     '', '8.0')],
            'gen2/networking/WirelessController': [ShellTemplate('gen2/networking/WirelessController',
                                                                 'TOSCA based template for standard WirelessController devices/virtual appliances',
                                                                 '', '8.0')]})
        flag_value = None

        standards = Mock()
        standards.fetch.return_value = {}

        list_command_executor = ListCommandExecutor(
            template_retriever=FilteredTemplateRetriever(flag_value, template_retriever), standards=standards)

        # Act
        list_command_executor.list()

        # Assert
        echo_mock.assert_any_call('''
As of CloudShell 8.0, CloudShell uses 2nd generation shells, to view the list of 1st generation shells use: shellfoundry list --gen1.
For more information, please visit our devguide: https://qualisystems.github.io/devguide/''')

    @patch('click.echo')
    @patch('shellfoundry.commands.list_command.AsciiTable.column_max_width')
    @patch('shellfoundry.commands.list_command.Configuration')
    @httpretty.activate
    def test_templates_are_filtered_based_upon_the_result_of_cs_standards(self, conf_class, max_width_mock, echo_mock):
        # Arrange
        configuration = MagicMock(read=MagicMock(return_value=MagicMock(online_mode="True")))
        conf_class.return_value = configuration
        max_width_mock.return_value = 40
        templates = """templates:
    - name : gen1/resource
      description : base description
      repository : https://github.com/QualiSystems/shell-resource-standard
      params:
        project_name :
      min_cs_ver: 7.0
    - name : gen1/switch
      description : switch description
      repository : https://github.com/QualiSystems/shell-switch-standard
      params:
        project_name :
      min_cs_ver: 7.0
    - name : gen2/resource
      params:
        project_name :
        family_name:
      description : 2nd generation shell template for a standard resource
      repository : https://github.com/QualiSystems/shellfoundry-tosca-resource-template
      min_cs_ver: 8.0
    - name : gen2/networking/switch
      params:
        project_name :
        family_name: Switch
      description : 2nd generation shell template for a standard switch
      repository : https://github.com/QualiSystems/shellfoundry-tosca-networking-template
      min_cs_ver: 8.0
    - name : gen2/networking/wireless-controller
      params:
        project_name :
        family_name: WirelessController
      description : 2nd generation shell template for a standard wireless controller
      repository : https://github.com/QualiSystems/shellfoundry-tosca-networking-template
      min_cs_ver: 8.0"""

        flag_value = 'all'

        standards = Mock()
        standards.fetch.return_value = {"resource": ['5.0.0']}

        template_retriever = FilteredTemplateRetriever(flag_value, TemplateRetriever())

        httpretty.register_uri(httpretty.GET, TEMPLATES_YML, body=templates)

        list_command_executor = ListCommandExecutor(template_retriever=template_retriever, standards=standards)

        # Act
        list_command_executor.list()

        # Assert
        echo_mock.assert_any_call(
            u' Template Name  CloudShell Ver.  Description                         \n'
            u'---------------------------------------------------------------------\n'
            u' gen1/resource  7.0 and up       base description                    \n'
            u' gen1/switch    7.0 and up       switch description                  \n'
            u' gen2/resource  8.0 and up       2nd generation shell template for a \n'
            u'                                 standard resource                   ')

    @patch('click.echo')
    @patch('shellfoundry.commands.list_command.AsciiTable.column_max_width')
    @patch('shellfoundry.commands.list_command.Configuration')
    @httpretty.activate
    def test_templates_are_filtered_based_upon_the_result_of_cs_standards_gen2(self, conf_class, max_width_mock,
                                                                               echo_mock):
        # Arrange
        configuration = MagicMock(read=MagicMock(return_value=MagicMock(online_mode="True")))
        conf_class.return_value = configuration
        max_width_mock.return_value = 40
        templates = """templates:
        - name : gen1/resource
          description : base description
          repository : https://github.com/QualiSystems/shell-resource-standard
          params:
            project_name :
          min_cs_ver: 7.0
        - name : gen1/switch
          description : switch description
          repository : https://github.com/QualiSystems/shell-switch-standard
          params:
            project_name :
          min_cs_ver: 7.0
        - name : gen2/resource
          params:
            project_name :
            family_name:
          description : 2nd generation shell template for a standard resource
          repository : https://github.com/QualiSystems/shellfoundry-tosca-resource-template
          min_cs_ver: 8.0
        - name : gen2/networking/switch
          params:
            project_name :
            family_name: Switch
          description : 2nd generation shell template for a standard switch
          repository : https://github.com/QualiSystems/shellfoundry-tosca-networking-template
          min_cs_ver: 8.0
        - name : gen2/networking/wireless-controller
          params:
            project_name :
            family_name: WirelessController
          description : 2nd generation shell template for a standard wireless controller
          repository : https://github.com/QualiSystems/shellfoundry-tosca-networking-template
          min_cs_ver: 8.0"""

        flag_value = 'gen2'

        standards = Mock()
        standards.fetch.return_value = {"networking": ['5.0.0']}

        template_retriever = FilteredTemplateRetriever(flag_value, TemplateRetriever())

        httpretty.register_uri(httpretty.GET, TEMPLATES_YML, body=templates)

        list_command_executor = ListCommandExecutor(template_retriever=template_retriever, standards=standards)

        # Act
        list_command_executor.list()

        # Assert
        echo_mock.assert_any_call(
            u' Template Name                        CloudShell Ver.  Description                         \n'
            u'-------------------------------------------------------------------------------------------\n'
            u' gen2/networking/switch               8.0 and up       2nd generation shell template for a \n'
            u'                                                       standard switch                     \n'
            u' gen2/networking/wireless-controller  8.0 and up       2nd generation shell template for a \n'
            u'                                                       standard wireless controller        ')


class TestListCommandWithFakeFs(fake_filesystem_unittest.TestCase):
    def setUp(self):
        self.setUpPyfakefs()

    @staticmethod
    def get_8_0_templates_output():
        return (
            u' Template Name                        CloudShell Ver.  Description                                                 \n'
            u'-------------------------------------------------------------------------------------------------------------------\n'
            u' gen1/compute                         7.0 and up       1st generation shell template for compute servers           \n'
            u' gen1/deployed-app                    7.0 and up       1st generation shell template for a deployed app            \n'
            u' gen1/firewall                        7.0 and up       1st generation shell template for a standard firewall       \n'
            u' gen1/networking/router               7.0 and up       1st generation shell template for a standard router         \n'
            u' gen1/networking/switch               7.0 and up       1st generation shell template for a standard switch         \n'
            u' gen1/pdu                             7.0 and up       1st generation shell template for a standard pdu            \n'
            u' gen1/resource                        7.0 and up       1st generation shell template for basic inventory resources \n'
            u' gen1/resource-clean                  7.0 and up       1st generation shell template for basic inventory resources \n'
            u'                                                       (without sample commands)                                   \n'
            u' gen2/compute                         8.0 and up       2nd generation shell template for compute servers           \n'
            u' gen2/deployed-app                    8.0 and up       2nd generation shell template for a deployed app            \n'
            u' gen2/firewall                        8.0 and up       2nd generation shell template for firewall resources        \n'
            u' gen2/networking/router               8.0 and up       2nd generation shell template for a standard router         \n'
            u' gen2/networking/switch               8.0 and up       2nd generation shell template for a standard switch         \n'
            u' gen2/networking/wireless-controller  8.0 and up       2nd generation shell template for a standard wireless       \n'
            u'                                                       controller                                                  \n'
            u' gen2/pdu                             8.0 and up       2nd generation shell template for a standard pdu            \n'
            u' gen2/resource                        8.0 and up       2nd generation shell template for basic inventory resources \n'
            u' layer-1-switch                       7.0 and up       A native shell template for layer 1 switches                ')

    @patch('click.echo')
    @patch('shellfoundry.commands.list_command.AsciiTable.column_max_width')
    def test_get_cs_standards_unavailable_shows_cs_8_0_shipped_templates(self, max_width_mock, echo_mock):
        # Assert
        max_width_mock.return_value = 60

        from shellfoundry import ALTERNATIVE_TEMPLATES_PATH
        self.fs.add_real_file(ALTERNATIVE_TEMPLATES_PATH)

        standards = Mock(fetch=Mock(side_effect=FeatureUnavailable()))

        template_retriever = FilteredTemplateRetriever('all', TemplateRetriever())

        list_command_executor = ListCommandExecutor(template_retriever=template_retriever, standards=standards)

        # Act
        list_command_executor.list()

        # Assert
        templates_output = self.get_8_0_templates_output()
        echo_mock.assert_any_call(templates_output)
