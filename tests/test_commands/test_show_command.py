import click
import unittest

from mock import patch, Mock, PropertyMock, call
from shellfoundry.commands.show_command import ShowCommandExecutor
from shellfoundry.utilities.template_retriever import TemplateRetriever
from shellfoundry.utilities.template_versions import TemplateVersions
from shellfoundry.models.shell_template import ShellTemplate

patch.object = patch.object


class TestShowCommandExecutor(unittest.TestCase):
    @patch('shellfoundry.commands.show_command.click.echo')
    def test_show_template_one_version_shows_as_latest(self, echo_mock):
        # Arrange
        template_name = 'tosca/networking/switch'
        raw_response = """[
  {
    "name": "master"
  },
  {
    "name": "1.0"
  }
]"""
        shell_template = ShellTemplate('tosca/networking/switch',
                                       'some description',
                                       'mock://tosca/networking/switch', '8.0')
        template_retriever_mock = Mock(spec=TemplateRetriever, autospec=True)
        template_retriever_mock.get_templates.return_value = {'tosca/networking/switch': shell_template}

        # Act
        with patch('shellfoundry.commands.show_command.requests.get') as get_response_mock:
            type(get_response_mock.return_value).status_code = PropertyMock(return_value=200)
            type(get_response_mock.return_value).text = PropertyMock(return_value=raw_response)
            ShowCommandExecutor(template_retriever_mock).show(template_name)

        # Assert
        echo_mock.assert_called_once_with('1.0 (latest)')

    @patch('shellfoundry.commands.show_command.click.echo')
    def test_show_template_versions_are_sorted_from_latest_to_earliest_version(self, echo_mock):
        # Arrange
        template_name = 'tosca/networking/switch'
        raw_response = """[
          {
            "name": "master"
          },
          {
            "name": "1.0"
          },
          {
            "name": "1.1"
          }
        ]"""

        shell_template = ShellTemplate('tosca/networking/switch',
                                       'some description',
                                       'mock://tosca/networking/switch', '8.0')
        template_retriever_mock = Mock(spec=TemplateRetriever, autospec=True)
        template_retriever_mock.get_templates.return_value = {'tosca/networking/switch': shell_template}

        # Act
        with patch('shellfoundry.commands.show_command.requests.get') as get_response_mock:
            type(get_response_mock.return_value).status_code = PropertyMock(return_value=200)
            type(get_response_mock.return_value).text = PropertyMock(return_value=raw_response)
            ShowCommandExecutor(template_retriever_mock).show(template_name)

        # Assert
        calls = [call('1.1 (latest)'), call('1.0')]
        echo_mock.assert_has_calls(calls, any_order=False)

    def test_show_template_shows_fail_message_when_template_does_not_exist(self):
        # Arrange
        template_name = 'idonot/exist'

        shell_template = ShellTemplate('notheright/one',
                                       'some description',
                                       'mock://not/the/right/one', '8.0')
        template_retriever_mock = Mock(spec=TemplateRetriever, autospec=True)
        template_retriever_mock.get_templates.return_value = {'tosca/networking/switch': shell_template}

        # Act
        with self.assertRaises(click.ClickException) as context:
            ShowCommandExecutor(template_retriever_mock).show(template_name)

        # Assert
        self.assertTrue("The template '{}' does not exist, please specify a valid 2nd Gen shell template.".format(
            template_name) in context.exception)

    def test_repository_url_is_empty_raises_error(self):
        # Arrange
        template_name = 'tosca/networking/switch'

        repository = ''
        shell_template = ShellTemplate('tosca/networking/switch',
                                       'some description',
                                       repository, '8.0')
        template_retriever_mock = Mock(spec=TemplateRetriever, autospec=True)
        template_retriever_mock.get_templates.return_value = {'tosca/networking/switch': shell_template}

        # Act
        with self.assertRaises(click.ClickException) as context:
            ShowCommandExecutor(template_retriever_mock).show(template_name)

        # Assert
        self.assertTrue('Repository url is empty' in context.exception)

    def test_show_command_versions_request_failed_raises_error(self):
        # Arrange
        template_name = 'tosca/networking/switch'

        shell_template = ShellTemplate('tosca/networking/switch',
                                       'some description',
                                       'mock://tosca/networking/switch', '8.0')
        template_retriever_mock = Mock(spec=TemplateRetriever, autospec=True)
        template_retriever_mock.get_templates.return_value = {'tosca/networking/switch': shell_template}

        # Act
        with patch('shellfoundry.commands.show_command.requests.get') as get_response_mock, \
            self.assertRaises(click.ClickException) as context:
            type(get_response_mock.return_value).status_code = PropertyMock(return_value=400)
            ShowCommandExecutor(template_retriever_mock).show(template_name)

        # Assert
        self.assertTrue('Failed to receive versions from host' in context.exception)

    def test_show_command_raise_no_versions_found_when_there_are_no_versions_other_than_master(self):
        # Arrange
        template_name = 'tosca/networking/switch'
        raw_response = """[
          {
            "name": "master"
          }
        ]"""

        shell_template = ShellTemplate('tosca/networking/switch',
                                       'some description',
                                       'mock://tosca/networking/switch', '8.0')
        template_retriever_mock = Mock(spec=TemplateRetriever, autospec=True)
        template_retriever_mock.get_templates.return_value = {'tosca/networking/switch': shell_template}

        # Act
        with patch('shellfoundry.commands.show_command.requests.get') as get_response_mock, \
            self.assertRaises(click.ClickException) as context:
            type(get_response_mock.return_value).status_code = PropertyMock(return_value=200)
            type(get_response_mock.return_value).text = PropertyMock(return_value=raw_response)
            ShowCommandExecutor(template_retriever_mock).show(template_name)

        # Assert
        self.assertTrue("No versions have been found for this template" in context.exception)

    def test_show_command_raise_no_versions_found_when_there_are_no_versions_at_all(self):
        # Arrange
        template_name = 'tosca/networking/switch'
        raw_response = """[]"""

        shell_template = ShellTemplate('tosca/networking/switch',
                                       'some description',
                                       'mock://tosca/networking/switch', '8.0')
        template_retriever_mock = Mock(spec=TemplateRetriever, autospec=True)
        template_retriever_mock.get_templates.return_value = {'tosca/networking/switch': shell_template}

        # Act
        with patch('shellfoundry.commands.show_command.requests.get') as get_response_mock, \
            self.assertRaises(click.ClickException) as context:
            type(get_response_mock.return_value).status_code = PropertyMock(return_value=200)
            type(get_response_mock.return_value).text = PropertyMock(return_value=raw_response)
            ShowCommandExecutor(template_retriever_mock).show(template_name)

        # Assert
        self.assertTrue("No versions have been found for this template" in context.exception)
