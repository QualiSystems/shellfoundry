import unittest
from unittest import skip

from mock import Mock, patch

from shellfoundry.commands.new_command import NewCommandExecutor
from shellfoundry.models.shell_template import ShellTemplate


class TestMainCli(unittest.TestCase):

    def test_not_existing_template_exception_thrown(self):
        # Arrange
        template_retriever = Mock()
        template_retriever.get_templates = Mock(return_value={'default': None})
        command_executor = NewCommandExecutor(template_retriever=template_retriever)

        # Act + Assert
        self.assertRaises(Exception, command_executor.new, 'nut_shell', 'NOT_EXISTING_TEMPLATE')

    @patch('cookiecutter.main.cookiecutter')
    @skip('need to fix patching')
    def test_cookiecutter_called_for_existing_template(self, mock_cookiecutter):
        # Arrange
        template_retriever = Mock()
        template_retriever.get_templates = Mock(return_value={'base': ShellTemplate('base', '', 'url')})
        command_executor = NewCommandExecutor(template_retriever=template_retriever)

        # Act
        command_executor.new('nut_shell', 'base')

        # Assert
        mock_cookiecutter.assert_called_once_with('url', no_input=True, extra_context={u'project_name': 'base'})
