import unittest
from mock import Mock, patch
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
        echo_mock.assert_called_once_with(u'\r\nSupported templates are:\r\n\r\n'
                                          u' base:                 description')

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
            u'\r\nSupported templates are:\r\n\r\n'
            u' base:                 base description\r\n'
            u' switch:               switch description')
