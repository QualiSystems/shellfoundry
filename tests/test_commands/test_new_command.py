import os
import httpretty

from click import BadParameter
from click import UsageError
from mock import Mock, patch
from pyfakefs import fake_filesystem_unittest
from quali.testing.extensions import mocking_extensions
from requests.exceptions import SSLError
from shellfoundry.commands.new_command import NewCommandExecutor
from shellfoundry.models.shell_template import ShellTemplate
from shellfoundry.utilities.cookiecutter_integration import CookiecutterTemplateCompiler
from shellfoundry.utilities.template_retriever import TemplateRetriever
from shellfoundry.utilities.repository_downloader import RepositoryDownloader
from shellfoundry.utilities.temp_dir_context import TempDirContext
from shellfoundry.utilities.standards import StandardVersionsFactory, StandardVersions
from shellfoundry.utilities.template_versions import TemplateVersions

patch.object = patch.object


def mock_template_zip_file():
    # possible test would be to actually replicate a real template in memory and not just use random files
    # or somehow reading a template from filesystem without clashing with pyfakefs stubs
    import StringIO
    import zipfile
    imf = StringIO.StringIO()
    with zipfile.ZipFile(imf, mode='w', compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(zipfile.ZipInfo('root'), '')  # adding empty root directory
        zf.writestr('file1.txt', "hi")
    imf.seek(0)
    return imf


class TestMainCli(fake_filesystem_unittest.TestCase):
    def setUp(self):
        self.setUpPyfakefs()
        mocking_extensions.bootstrap()

        from requests.utils import DEFAULT_CA_BUNDLE_PATH
        self.fs.CreateFile(DEFAULT_CA_BUNDLE_PATH)

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
        self.assertRaisesRegexp(UsageError, "offline",  command_executor.new, 'nut_shell', 'base', 'master')

    def test_not_existing_local_template_dir_thrown(self):
        # Arrange
        template_retriever = Mock()
        template_retriever.get_templates = Mock(return_value={'base': ShellTemplate('base', '', 'url', '7.0')})

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
                               'new_shell', 'local:{template_dir}'.format(template_dir='shell_template_root'), 'master')

    def test_cookiecutter_called_for_existing_template(self):
        # Arrange
        template_retriever = Mock()
        template_retriever.get_templates = Mock(
            return_value={'base': ShellTemplate('base', '', 'https://fakegithub.com/user/repo', '7.0')})

        repo_downloader = Mock()
        repo_downloader.download_template.return_value = 'repo_path'

        template_compiler = Mock()

        command_executor = NewCommandExecutor(template_retriever=template_retriever,
                                              repository_downloader=repo_downloader,
                                              template_compiler=template_compiler)
        # Act
        command_executor.new('nut_shell', 'base', 'master')

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
        template_retriever.get_templates = Mock(return_value={'base': ShellTemplate('base', '', 'url', '7.0')})

        repo_downloader = Mock()
        repo_downloader.download_template.return_value = 'repo_path'

        template_compiler = Mock()

        command_executor = NewCommandExecutor(template_retriever=template_retriever,
                                              repository_downloader=repo_downloader,
                                              template_compiler=template_compiler)

        self.fs.CreateDirectory('linux-shell')
        os.chdir('linux-shell')

        # Act
        command_executor.new(os.path.curdir, 'base', 'master')

        template_compiler.compile_template.smarter_assert_called_once_with(
            CookiecutterTemplateCompiler.compile_template,
            shell_name='linux-shell',
            template_path='repo_path',
            extra_context={},
            running_on_same_folder=True)

    def test_can_generate_local_template_into_same_directory(self):
        # Arrange
        template_retriever = Mock()
        template_retriever.get_templates = Mock(return_value={'base': ShellTemplate('base', '', 'url', '7.0')})

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
        command_executor.new(os.path.curdir, 'local:{template_dir}'.format(template_dir=local_template), 'master')

        template_compiler.compile_template.smarter_assert_called_once_with(
            CookiecutterTemplateCompiler.compile_template,
            shell_name=shell_dir,
            template_path=local_template,
            extra_context={},
            running_on_same_folder=True)

    def test_can_generate_shell_from_local_template(self):
        # Arrange
        template_retriever = Mock()
        template_retriever.get_templates = Mock(return_value={'base': ShellTemplate('base', '', 'url', '7.0')})

        repo_downloader = Mock()
        repo_downloader.download_template.return_value = 'repo_path'

        template_compiler = Mock()

        command_executor = NewCommandExecutor(template_retriever=template_retriever,
                                              repository_downloader=repo_downloader,
                                              template_compiler=template_compiler)

        local_template = self.fs.CreateDirectory('shell_template_root').name

        # Act
        command_executor.new('new_shell', 'local:{template_dir}'.format(template_dir=local_template), 'master')

        template_compiler.compile_template.smarter_assert_called_once_with(
            CookiecutterTemplateCompiler.compile_template,
            shell_name='new_shell',
            template_path='shell_template_root',
            extra_context={},
            running_on_same_folder=False)

    @httpretty.activate
    def test_integration_can_generate_shell_from_specific_version(self):
        # Arrange
        templates = {'tosca/resource/test': ShellTemplate('test-resource', '', 'url/test', '8.1', 'resource')}
        repo_info = ('quali', 'resource-test')

        zipfile = mock_template_zip_file()
        httpretty.register_uri(httpretty.GET, "https://api.github.com/repos/quali/resource-test/zipball/1.1",
                               body=zipfile.read(), content_type='application/zip',
                               content_disposition="attachment; filename=quali-resource-test-dd2ba19.zip", stream=True)
        template_compiler = Mock()

        standards = Mock()
        standards.fetch.return_value = [{'StandardName': "cloudshell_resource_standard", 'Versions': ['1.0.0', '1.0.1']}]

        template_versions = ['master', '1.0.0', '1.0.1']

        # Act
        with patch.object(TemplateRetriever, 'get_templates', return_value=templates), \
             patch('shellfoundry.utilities.template_url._parse_repo_url', return_value=repo_info), \
             patch.object(TempDirContext, '__enter__', return_value=self.fs.CreateDirectory('mock_temp').name):
            NewCommandExecutor(template_retriever=TemplateRetriever(),
                               repository_downloader=RepositoryDownloader(),
                               template_compiler=template_compiler,
                               standards=standards,
                               standard_versions=StandardVersionsFactory())\
                .new('new_shell', 'tosca/resource/test', '1.1')


        # Assert
        template_compiler.compile_template.smarter_assert_called_once_with(
            CookiecutterTemplateCompiler.compile_template,
            shell_name='new_shell',
            template_path=os.path.join('mock_temp', 'root'),
            extra_context={},
            running_on_same_folder=False)


    @httpretty.activate
    def test_fail_to_generate_shell_when_requested_version_does_not_exists(self):
        # Arrange
        templates = {'tosca/resource/test': ShellTemplate('test-resource', '', 'url/test', '8.1', 'resource')}
        repo_info = ('quali', 'resource-test')

        httpretty.register_uri(httpretty.GET, "https://api.github.com/repos/quali/resource-test/zipball/1.1",
                               body='', status=404, stream=True)
        template_compiler = Mock()

        standards = Mock()
        standards.fetch.return_value = [{'StandardName': "cloudshell_resource_standard", 'Versions': ['1.0.0', '1.0.1']}]

        template_versions = ['master', '1.0.0', '1.0.1']

        # Act
        with patch.object(TemplateRetriever, 'get_templates', return_value=templates), \
             patch('shellfoundry.utilities.template_url._parse_repo_url', return_value=repo_info), \
             patch.object(TempDirContext, '__enter__', return_value=self.fs.CreateDirectory('mock_temp').name),\
             patch.object(TemplateVersions, 'get_versions_of_template', return_value=template_versions),\
             self.assertRaises(BadParameter) as context:
            NewCommandExecutor(template_retriever=TemplateRetriever(),
                               repository_downloader=RepositoryDownloader(),
                               template_compiler=template_compiler,
                               standards=standards,
                               standard_versions=StandardVersionsFactory()) \
                .new('new_shell', 'tosca/resource/test', '1.1')

        # Assert
        self.assertTrue('Requested standard version (\'1.1\') does not match template version. \n'
                        'Available versions for test-resource: 1.0.0, 1.0.1' in context.exception,
                        'Actual: {}'.format(context.exception))

    @httpretty.activate
    def test_integration_latest_version_is_default_when_version_was_not_specified(self):
        # Arrange
        templates = {'tosca/resource/test': ShellTemplate('test-resource', '', 'url', '8.1', 'resource')}
        repo_info = ('quali', 'resource-test')

        zipfile = mock_template_zip_file()
        httpretty.register_uri(httpretty.GET, "https://api.github.com/repos/quali/resource-test/branches",
                               body='''[{"name": "master"}, {"name": "1.0"}, {"name": "1.1"}, {"name": "2.0.1"}]''')
        httpretty.register_uri(httpretty.GET, "https://api.github.com/repos/quali/resource-test/zipball/2.0.1",
                               body=zipfile.read(), content_type='application/zip',
                               content_disposition="attachment; filename=quali-resource-test-dd2ba19.zip", stream=True)
        template_compiler = Mock()

        standards = Mock()
        standards.fetch.return_value = [{'StandardName': "cloudshell_resource_standard", 'Versions': ['2.0.0', '2.0.1']}]

        # Act
        with patch.object(TemplateRetriever, 'get_templates', return_value=templates), \
             patch('shellfoundry.utilities.template_url._parse_repo_url', return_value=repo_info), \
             patch.object(TempDirContext, '__enter__', return_value=self.fs.CreateDirectory('mock_temp').name):
            NewCommandExecutor(template_retriever=TemplateRetriever(),
                               repository_downloader=RepositoryDownloader(),
                               template_compiler=template_compiler,
                               standards=standards,
                               standard_versions=StandardVersionsFactory()) \
                .new('new_shell', 'tosca/resource/test')

        # Assert
        template_compiler.compile_template.smarter_assert_called_once_with(
            CookiecutterTemplateCompiler.compile_template,
            shell_name='new_shell',
            template_path=os.path.join('mock_temp', 'root'),
            extra_context={},
            running_on_same_folder=False)
