import unittest

from mock import Mock, patch

from shellfoundry.commands.list_command import ListCommandExecutor
from shellfoundry.models.shell_template import ShellTemplate


class TestListCommand(unittest.TestCase):

    @patch('click.echo')
    def test_list_command_does_not_fail(self, echo_mock):
        # Arrange
        template_retriever = Mock()
        template_retriever.get_templates = Mock(return_value={'base': ShellTemplate('base', '', '')})

        list_command_executor = ListCommandExecutor(template_retriever)

        # Act
        list_command_executor.list()

        # Assert
        echo_mock.assert_called_once_with(u'Supported templates are: \r\n base')
