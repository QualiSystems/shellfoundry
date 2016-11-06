import unittest

from click import UsageError
from mock import Mock, patch
from requests.exceptions import SSLError
from shellfoundry.commands.list_command import ListCommandExecutor
from shellfoundry.models.shell_template import ShellTemplate
from collections import OrderedDict


class TestListCommand(unittest.TestCase):
    @patch('click.echo')
    def test_single_template_is_displayed(self, echo_mock):
        # Arrange
        template_retriever = Mock()
        template_retriever.get_templates = Mock(return_value={'base': ShellTemplate('base', 'description', '')})

        list_command_executor = ListCommandExecutor(template_retriever)

        # Act
        list_command_executor.list()

        # Assert
        echo_mock.assert_called_once_with(u' Template Name  Description \n'
                                          u'----------------------------\n'
                                          u' base           description ')

    def test_shows_informative_message_when_offline(self):
        # Arrange
        template_retriever = Mock()
        template_retriever.get_templates.side_effect = SSLError()
        list_command_executor = ListCommandExecutor(template_retriever)

        # Assert
        self.assertRaisesRegexp(UsageError, "offline", list_command_executor.list)

    @patch('click.echo')
    def test_two_templates_are_displayed(self, echo_mock):
        # Arrange
        template_retriever = Mock()
        template_retriever.get_templates = Mock(return_value=OrderedDict(
            [('base', ShellTemplate('base', 'base description', '')),
             ('switch', ShellTemplate('switch', 'switch description', ''))]))

        list_command_executor = ListCommandExecutor(template_retriever)

        # Act
        list_command_executor.list()

        # Assert
        echo_mock.assert_called_once_with(
            u' Template Name  Description        \n'
            u'-----------------------------------\n'
            u' base           base description   \n'
            u' switch         switch description ')

    @patch('click.echo')
    def test_two_long_named_templates_are_displayed_on_normal_window(self, echo_mock):
        # Arrange
        template_retriever = Mock()
        template_retriever.get_templates = Mock(return_value=OrderedDict(
            [('tosca/networking/switch', ShellTemplate('tosca/networking/switch', 'TOSCA based template for standard Switch devices/virtual appliances', '')),
             ('tosca/networking/WirelessController', ShellTemplate('tosca/networking/WirelessController', 'TOSCA based template for standard WirelessController devices/virtual appliances', ''))]))

        list_command_executor = ListCommandExecutor(template_retriever)

        # Act
        list_command_executor.list()

        # Assert
        echo_mock.assert_called_once_with(
            u' Template Name                        Description                              \n'
            u'-------------------------------------------------------------------------------\n'
            u' tosca/networking/switch              TOSCA based template for standard Switch \n'
            u'                                      devices/virtual appliances               \n'
            u' tosca/networking/WirelessController  TOSCA based template for standard        \n'
            u'                                      WirelessController devices/virtual       \n'
            u'                                      appliances                               ')

