import os

from click import BadParameter
from click import UsageError
from mock import Mock
from pyfakefs import fake_filesystem_unittest
from quali.testing.extensions import mocking_extensions
from requests.exceptions import SSLError
from shellfoundry.commands.new_command import NewCommandExecutor
from shellfoundry.models.shell_template import ShellTemplate
from shellfoundry.utilities.cookiecutter_integration import CookiecutterTemplateCompiler


class TestMainCli(fake_filesystem_unittest.TestCase):
    def setUp(self):
        self.setUpPyfakefs()
        mocking_extensions.bootstrap()

    def test_not_existing_template_exception_thrown(self):
        # Arrange
        template_retriever = Mock()
        template_retriever.get_templates = Mock(return_value={'default': None})
        command_executor = NewCommandExecutor(template_retriever=template_retriever)

        # Act + Assert
        self.assertRaises(Exception, command_executor.new, 'nut_shell', 'NOT_EXISTING_TEMPLATE')

    def test_shows_informative_message_when_offline(self):
        # Arrange
        template_retriever = Mock()
        template_retriever.get_templates.side_effect = \
            SSLError()

        repo_downloader = Mock()
        repo_downloader.download_template.return_value = 'repo_path'

        template_compiler = Mock()

        command_executor = NewCommandExecutor(template_retriever=template_retriever,
                                              repository_downloader=repo_downloader,
                                              template_compiler=template_compiler)
        # Act
        self.assertRaisesRegexp(UsageError, "offline",  command_executor.new, 'nut_shell', 'base')

    def test_not_existing_local_template_dir_thrown(self):
        # Arrange
        template_retriever = Mock()
        template_retriever.get_templates = Mock(return_value={'base': ShellTemplate('base', '', 'url')})

        repo_downloader = Mock()
        repo_downloader.download_template.return_value = 'repo_path'

        template_compiler = Mock()

        command_executor = NewCommandExecutor(template_retriever=template_retriever,
                                              repository_downloader=repo_downloader,
                                              template_compiler=template_compiler)

        # Act
        # Message should at least contain the bad dir name
        self.assertRaisesRegexp(BadParameter, 'shell_template_root',
                               command_executor.new,
                               'new_shell', 'local:{template_dir}'.format(template_dir='shell_template_root'))

    def test_cookiecutter_called_for_existing_template(self):
        # Arrange
        template_retriever = Mock()
        template_retriever.get_templates = Mock(
            return_value={'base': ShellTemplate('base', '', 'https://fakegithub.com/user/repo')})

        repo_downloader = Mock()
        repo_downloader.download_template.return_value = 'repo_path'

        template_compiler = Mock()

        command_executor = NewCommandExecutor(template_retriever=template_retriever,
                                              repository_downloader=repo_downloader,
                                              template_compiler=template_compiler)
        # Act
        command_executor.new('nut_shell', 'base')

        # Assert
        template_compiler.compile_template.smarter_assert_called_once_with(
            CookiecutterTemplateCompiler.compile_template,
            shell_name='nut_shell',
            template_path='repo_path',
            extra_context={},
            running_on_same_folder=False)

    def test_can_generate_online_shell_into_same_directory(self):
        # Arrange
        template_retriever = Mock()
        template_retriever.get_templates = Mock(return_value={'base': ShellTemplate('base', '', 'url')})

        repo_downloader = Mock()
        repo_downloader.download_template.return_value = 'repo_path'

        template_compiler = Mock()

        command_executor = NewCommandExecutor(template_retriever=template_retriever,
                                              repository_downloader=repo_downloader,
                                              template_compiler=template_compiler)

        self.fs.CreateDirectory('linux-shell')
        os.chdir('linux-shell')

        # Act
        command_executor.new(os.path.curdir, 'base')

        template_compiler.compile_template.smarter_assert_called_once_with(
            CookiecutterTemplateCompiler.compile_template,
            shell_name='linux-shell',
            template_path='repo_path',
            extra_context={},
            running_on_same_folder=True)

    def test_can_generate_local_template_into_same_directory(self):
        # Arrange
        template_retriever = Mock()
        template_retriever.get_templates = Mock(return_value={'base': ShellTemplate('base', '', 'url')})

        repo_downloader = Mock()
        repo_downloader.download_template.return_value = 'repo_path'

        template_compiler = Mock()

        command_executor = NewCommandExecutor(template_retriever=template_retriever,
                                              repository_downloader=repo_downloader,
                                              template_compiler=template_compiler)

        local_template = os.path.abspath(self.fs.CreateDirectory('shell_template_root').name)

        shell_dir = self.fs.CreateDirectory('linux-shell').name
        os.chdir(shell_dir)

        # Act
        command_executor.new(os.path.curdir, 'local:{template_dir}'.format(template_dir=local_template))

        template_compiler.compile_template.smarter_assert_called_once_with(
            CookiecutterTemplateCompiler.compile_template,
            shell_name=shell_dir,
            template_path=local_template,
            extra_context={},
            running_on_same_folder=True)

    def test_can_generate_shell_from_local_template(self):
        # Arrange
        template_retriever = Mock()
        template_retriever.get_templates = Mock(return_value={'base': ShellTemplate('base', '', 'url')})

        repo_downloader = Mock()
        repo_downloader.download_template.return_value = 'repo_path'

        template_compiler = Mock()

        command_executor = NewCommandExecutor(template_retriever=template_retriever,
                                              repository_downloader=repo_downloader,
                                              template_compiler=template_compiler)

        local_template = self.fs.CreateDirectory('shell_template_root').name

        # Act
        command_executor.new('new_shell', 'local:{template_dir}'.format(template_dir=local_template))

        template_compiler.compile_template.smarter_assert_called_once_with(
            CookiecutterTemplateCompiler.compile_template,
            shell_name='new_shell',
            template_path='shell_template_root',
            extra_context={},
            running_on_same_folder=False)
