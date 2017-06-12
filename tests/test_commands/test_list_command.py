import unittest

from click import UsageError
from mock import Mock, patch, PropertyMock
from requests.exceptions import SSLError
from shellfoundry.commands.list_command import ListCommandExecutor
from shellfoundry.models.shell_template import ShellTemplate
from shellfoundry.utilities.template_retriever import FilteredTemplateRetriever
from collections import OrderedDict


class TestListCommand(unittest.TestCase):
    @patch('click.echo')
    @patch('shellfoundry.commands.list_command.AsciiTable.column_max_width')
    def test_single_template_is_displayed(self, max_width_mock, echo_mock):
        # Arrange
        max_width_mock.return_value = 62  # mocking the max width to eliminate the distinction
        # between the running console size

        template_retriever = Mock()
        template_retriever.get_templates = Mock(
            return_value={'gen1/base': ShellTemplate('gen1/base', 'description', '', '7.0')})

        list_command_executor = ListCommandExecutor(template_retriever=template_retriever)

        # Act
        list_command_executor.list()

        # Assert
        echo_mock.assert_any_call(u' Template Name  CloudShell Ver.  Description \n'
                                  u'---------------------------------------------\n'
                                  u' gen1/base      7.0 and up       description ')

    def test_shows_informative_message_when_offline(self):
        # Arrange
        template_retriever = Mock()
        template_retriever.get_templates.side_effect = SSLError()
        list_command_executor = ListCommandExecutor(template_retriever=template_retriever)

        # Assert
        self.assertRaisesRegexp(UsageError, "offline", list_command_executor.list)

    @patch('click.echo')
    @patch('shellfoundry.commands.list_command.AsciiTable.column_max_width')
    def test_two_templates_are_displayed(self, max_width_mock, echo_mock):
        # Arrange
        max_width_mock.return_value = 62  # mocking the max width to eliminate the distinction
        # between the running console size

        template_retriever = Mock()
        template_retriever.get_templates = Mock(return_value=OrderedDict(
            [('gen1/base', ShellTemplate('gen1/base', 'base description', '', '7.0', 'base')),
             ('gen1/switch', ShellTemplate('gen1/switch', 'switch description', '', '7.0'))]))

        list_command_executor = ListCommandExecutor(template_retriever=template_retriever)

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
        template_retriever.get_templates = Mock(return_value=OrderedDict(
            [('gen2/networking/switch', ShellTemplate('gen2/networking/switch',
                                                      'TOSCA based template for standard Switch devices/virtual appliances',
                                                      '', '8.0')),
             ('gen2/networking/WirelessController', ShellTemplate('gen2/networking/WirelessController',
                                                                  'TOSCA based template for standard WirelessController devices/virtual appliances',
                                                                  '', '8.0'))]))

        list_command_executor = ListCommandExecutor(template_retriever=template_retriever)

        # Act
        list_command_executor.list()

        # Assert
        echo_mock.assert_any_call(
            u' Template Name                       CloudShell Ver.  Description                              \n'
            u'-----------------------------------------------------------------------------------------------\n'
            u' gen2/networking/switch              8.0 and up       TOSCA based template for standard Switch \n'
            u'                                                      devices/virtual appliances               \n'
            u' gen2/networking/WirelessController  8.0 and up       TOSCA based template for standard        \n'
            u'                                                      WirelessController devices/virtual       \n'
            u'                                                      appliances                               ')

    @patch('click.echo')
    @patch('shellfoundry.commands.list_command.AsciiTable.column_max_width')
    def test_console_size_small_description_wrapping_logic_ignored(self, max_width_mock, echo_mock):
        # Arrange
        max_width_mock.return_value = 0
        template_retriever = Mock()
        template_retriever.get_templates = Mock(return_value=OrderedDict(
            [('gen2/networking/switch', ShellTemplate('gen2/networking/switch',
                                                      'TOSCA based template for standard Switch devices/virtual appliances',
                                                      '', '8.0')),
             ('gen2/networking/WirelessController', ShellTemplate('gen2/networking/WirelessController',
                                                                  'TOSCA based template for standard WirelessController devices/virtual appliances',
                                                                  '', '8.0'))]))

        list_command_executor = ListCommandExecutor(template_retriever=template_retriever)

        # Act
        list_command_executor.list()

        # Assert
        echo_mock.assert_called_once_with(
            u' Template Name                       CloudShell Ver.  Description                                                                     \n'
            u'--------------------------------------------------------------------------------------------------------------------------------------\n'
            u' gen2/networking/switch              8.0 and up       TOSCA based template for standard Switch devices/virtual appliances             \n'
            u' gen2/networking/WirelessController  8.0 and up       TOSCA based template for standard WirelessController devices/virtual appliances ')

    @patch('click.echo')
    @patch('shellfoundry.commands.list_command.AsciiTable.column_max_width')
    def test_filter_by_tosca_shows_all_tosca_templates(self, max_width_mock, echo_mock):
        # Arrange
        max_width_mock.return_value = 40
        template_retriever = Mock()
        template_retriever.get_templates = Mock(return_value=OrderedDict(
            [('gen2/networking/switch', ShellTemplate('gen2/networking/switch',
                                                      'TOSCA based template for standard Switch devices/virtual appliances',
                                                      '', '8.0')),
             ('gen2/networking/WirelessController', ShellTemplate('gen2/networking/WirelessController',
                                                                  'TOSCA based template for standard WirelessController devices/virtual appliances',
                                                                  '', '8.0')),
             ('gen1/base', ShellTemplate('gen1/base', 'base description', '', '7.0')),
             ('gen1/switch', ShellTemplate('gen1/switch', 'switch description', '', '7.0'))]))
        flag_value = 'gen2'
        list_command_executor = ListCommandExecutor(
            template_retriever=FilteredTemplateRetriever(flag_value, template_retriever))

        # Act
        list_command_executor.list()

        # Assert
        echo_mock.assert_any_call(
            u' Template Name                       CloudShell Ver.  Description                              \n'
            u'-----------------------------------------------------------------------------------------------\n'
            u' gen2/networking/switch              8.0 and up       TOSCA based template for standard Switch \n'
            u'                                                      devices/virtual appliances               \n'
            u' gen2/networking/WirelessController  8.0 and up       TOSCA based template for standard        \n'
            u'                                                      WirelessController devices/virtual       \n'
            u'                                                      appliances                               ')

    @patch('click.echo')
    @patch('shellfoundry.commands.list_command.AsciiTable.column_max_width')
    def test_filter_by_legacy_shows_all_legacy_templates(self, max_width_mock, echo_mock):
        # Arrange
        max_width_mock.return_value = 62
        template_retriever = Mock()
        template_retriever.get_templates = Mock(return_value=OrderedDict(
            [('gen2/networking/switch', ShellTemplate('gen2/networking/switch',
                                                      'TOSCA based template for standard Switch devices/virtual appliances',
                                                      '', '8.0')),
             ('gen2/networking/WirelessController', ShellTemplate('gen2/networking/WirelessController',
                                                                  'TOSCA based template for standard WirelessController devices/virtual appliances',
                                                                  '', '8.0')),
             ('gen1/base', ShellTemplate('gen1/base', 'base description', '', '7.0')),
             ('gen1/switch', ShellTemplate('gen1/switch', 'switch description', '', '7.0'))]))
        flag_value = 'gen1'
        list_command_executor = ListCommandExecutor(
            template_retriever=FilteredTemplateRetriever(flag_value, template_retriever))

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
        template_retriever.get_templates = Mock(return_value=OrderedDict(
            [('gen1/base', ShellTemplate('gen1/base', 'base description', '', '7.0')),
             ('gen1/switch', ShellTemplate('gen1/switch', 'switch description', '', '7.0')),
             ('gen2/networking/switch', ShellTemplate('gen2/networking/switch',
                                                      'TOSCA based template for standard Switch devices/virtual appliances',
                                                      '', '8.0')),
             ('gen2/networking/WirelessController', ShellTemplate('gen2/networking/WirelessController',
                                                                  'TOSCA based template for standard WirelessController devices/virtual appliances',
                                                                  '', '8.0'))]))
        flag_value = 'all'
        list_command_executor = ListCommandExecutor(
            template_retriever=FilteredTemplateRetriever(flag_value, template_retriever))

        # Act
        list_command_executor.list()

        # Assert
        echo_mock.assert_any_call(
            u' Template Name                       CloudShell Ver.  Description                              \n'
            u'-----------------------------------------------------------------------------------------------\n'
            u' gen1/base                           7.0 and up       base description                         \n'
            u' gen1/switch                         7.0 and up       switch description                       \n'
            u' gen2/networking/switch              8.0 and up       TOSCA based template for standard Switch \n'
            u'                                                      devices/virtual appliances               \n'
            u' gen2/networking/WirelessController  8.0 and up       TOSCA based template for standard        \n'
            u'                                                      WirelessController devices/virtual       \n'
            u'                                                      appliances                               ')

    @patch('click.echo')
    @patch('shellfoundry.commands.list_command.AsciiTable.column_max_width')
    def test_list_shows_nothing_because_filter_is_set_for_templates_that_do_not_exist(self, max_width_mock,
                                                                                        echo_mock):
        # Arrange
        max_width_mock.return_value = 40
        template_retriever = Mock()
        template_retriever.get_templates = Mock(return_value=OrderedDict(
            [('gen2/networking/switch', ShellTemplate('gen2/networking/switch',
                                                      'TOSCA based template for standard Switch devices/virtual appliances',
                                                      '', '8.0')),
             ('gen2/networking/WirelessController', ShellTemplate('gen2/networking/WirelessController',
                                                                  'TOSCA based template for standard WirelessController devices/virtual appliances',
                                                                  '', '8.0'))]))
        flag_value = 'gen1'
        list_command_executor = ListCommandExecutor(
            template_retriever=FilteredTemplateRetriever(flag_value, template_retriever))

        # Act
        list_command_executor.list()

        # Assert
        echo_mock.assert_called_once_with('No templates matched the criteria')

    @patch('click.echo')
    @patch('shellfoundry.commands.list_command.AsciiTable.column_max_width')
    def test_devguide_text_note_appears_when_no_filter_was_selected(self, max_width_mock, echo_mock):
        # Arrange
        max_width_mock.return_value = 40
        template_retriever = Mock()
        template_retriever.get_templates = Mock(return_value=OrderedDict(
            [('gen2/networking/switch', ShellTemplate('gen2/networking/switch',
                                                      'TOSCA based template for standard Switch devices/virtual appliances',
                                                      '', '8.0')),
             ('gen2/networking/WirelessController', ShellTemplate('gen2/networking/WirelessController',
                                                                  'TOSCA based template for standard WirelessController devices/virtual appliances',
                                                                  '', '8.0'))]))
        flag_value = None
        list_command_executor = ListCommandExecutor(
            template_retriever=FilteredTemplateRetriever(flag_value, template_retriever))

        # Act
        list_command_executor.list()

        # Assert
        echo_mock.assert_any_call('''
As of CloudShell 8.0, CloudShell uses 2nd generation shells, to view the list of 1st generation shells use: shellfoundry list --gen1.
For more information, please visit our devguide: https://qualisystems.github.io/devguide/''')
