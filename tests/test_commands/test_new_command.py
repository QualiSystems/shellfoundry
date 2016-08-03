import os
from mock import Mock, patch
from pyfakefs import fake_filesystem_unittest
from shellfoundry.commands.new_command import NewCommandExecutor
from shellfoundry.models.shell_template import ShellTemplate


class TestMainCli(fake_filesystem_unittest.TestCase):
    def setUp(self):
        self.setUpPyfakefs()

    def test_not_existing_template_exception_thrown(self):
        # Arrange
        template_retriever = Mock()
        template_retriever.get_templates = Mock(return_value={'default': None})
        command_executor = NewCommandExecutor(template_retriever=template_retriever)

        # Act + Assert
        self.assertRaises(Exception, command_executor.new, 'nut_shell', 'NOT_EXISTING_TEMPLATE')

    @patch('shellfoundry.commands.new_command.cookiecutter')
    def test_cookiecutter_called_for_existing_template(self, mock_cookiecutter):
        # Arrange
        template_retriever = Mock()
        template_retriever.get_templates = Mock(return_value={'base': ShellTemplate('base', '', 'https://fakegithub.com/user/repo')})

        repo_downloader = Mock()
        repo_downloader.download_template.return_value = 'repo_path'

        command_executor = NewCommandExecutor(template_retriever=template_retriever, repository_downloader=repo_downloader)
        # Act
        command_executor.new('nut_shell', 'base')

        # Assert
        mock_cookiecutter.assert_called_once_with('repo_path', no_input=True, extra_context={u'project_name': 'nut_shell'})    \


    @patch('shellfoundry.commands.new_command.cookiecutter')
    def test_shell_should_be_created_in_the_same_directory(self, mock_cookiecutter):
        # Arrange
        template_retriever = Mock()
        template_retriever.get_templates = Mock(return_value={'base': ShellTemplate('base', '', 'url')})

        repo_downloader = Mock()
        repo_downloader.download_template.return_value = 'repo_path'

        command_executor = NewCommandExecutor(template_retriever=template_retriever,  repository_downloader=repo_downloader)

        self.fs.CreateDirectory('linux-shell')
        os.chdir('linux-shell')

        # Act
        command_executor.new('.', 'base')

        # Assert
        mock_cookiecutter.assert_called_once_with('repo_path',
                                                  no_input=True,
                                                  extra_context={u'project_name': 'linux-shell'},
                                                  overwrite_if_exists=True,
                                                  output_dir='..')
