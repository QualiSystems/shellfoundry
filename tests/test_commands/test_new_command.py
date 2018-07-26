#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import httpretty

from click import BadParameter
from click import UsageError
from mock import Mock, patch
from pyfakefs import fake_filesystem_unittest
from quali.testing.extensions import mocking_extensions
from requests.exceptions import SSLError
from cloudshell.rest.api import FeatureUnavailable
from shellfoundry import ALTERNATIVE_TEMPLATES_PATH, ALTERNATIVE_STANDARDS_PATH
from shellfoundry.commands.new_command import NewCommandExecutor
from shellfoundry.models.shell_template import ShellTemplate
from shellfoundry.utilities.cookiecutter_integration import CookiecutterTemplateCompiler
from shellfoundry.utilities.template_retriever import TemplateRetriever
from shellfoundry.utilities.repository_downloader import RepositoryDownloader
from shellfoundry.utilities.temp_dir_context import TempDirContext
from shellfoundry.utilities.standards import StandardVersionsFactory, Standards
from shellfoundry.utilities.template_versions import TemplateVersions
from shellfoundry.utilities.template_retriever import TEMPLATES_YML

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
                                              template_compiler=template_compiler,
                                              standards=Mock())
        # Act
        self.assertRaisesRegexp(UsageError, "offline", command_executor.new, 'nut_shell', 'base', 'master')

    def test_not_existing_local_template_dir_thrown(self):
        # Arrange
        template_retriever = Mock()
        template_retriever.get_templates = Mock(return_value={'base': ShellTemplate('base', '', 'url', '7.0')})

        repo_downloader = Mock()
        repo_downloader.download_template.return_value = 'repo_path'

        template_compiler = Mock()
        standards = Mock()
        standards.fetch.return_value = {}

        command_executor = NewCommandExecutor(template_retriever=template_retriever,
                                              repository_downloader=repo_downloader,
                                              standards=standards,
                                              template_compiler=template_compiler)

        # Act
        # Message should at least contain the bad dir name
        self.assertRaisesRegexp(BadParameter, 'shell_template_root',
                                command_executor.new,
                                'new_shell', 'local:{template_dir}'.format(template_dir='shell_template_root'),
                                'master')

    @patch("shellfoundry.commands.new_command.NewCommandExecutor._verify_template_standards_compatibility")
    def test_cookiecutter_called_for_existing_template(self, verification):
        # Arrange
        template_retriever = Mock()
        template_retriever.get_templates = Mock(
            return_value={'base': [ShellTemplate('base', '', 'https://fakegithub.com/user/repo', '7.0')]})

        repo_downloader = Mock()
        repo_downloader.download_template.return_value = 'repo_path'

        template_compiler = Mock()

        standards = Mock()
        standards.fetch.return_value = {}

        command_executor = NewCommandExecutor(template_retriever=template_retriever,
                                              repository_downloader=repo_downloader,
                                              template_compiler=template_compiler,
                                              standards=standards)

        # Act
        command_executor.new('nut_shell', 'base', 'master')

        # Assert
        template_compiler.compile_template.smarter_assert_called_once_with(
            CookiecutterTemplateCompiler.compile_template,
            shell_name='nut_shell',
            template_path='repo_path',
            extra_context={},
            running_on_same_folder=False)

    @patch("shellfoundry.commands.new_command.NewCommandExecutor._verify_template_standards_compatibility")
    def test_can_generate_online_shell_into_same_directory(self, verification):
        # Arrange
        template_retriever = Mock()
        template_retriever.get_templates = Mock(return_value={'base': [ShellTemplate('base', '', 'url', '7.0')]})

        repo_downloader = Mock()
        repo_downloader.download_template.return_value = 'repo_path'

        template_compiler = Mock()

        standards = Mock()
        standards.fetch.return_value = {}

        command_executor = NewCommandExecutor(template_retriever=template_retriever,
                                              repository_downloader=repo_downloader,
                                              template_compiler=template_compiler,
                                              standards=standards)

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

    @patch("shellfoundry.commands.new_command.NewCommandExecutor._verify_template_standards_compatibility")
    def test_can_generate_local_template_into_same_directory(self, verification):
        # Arrange
        template_retriever = Mock()
        template_retriever.get_templates = Mock(return_value={'base': [ShellTemplate('base', '', 'url', '7.0')]})

        repo_downloader = Mock()
        repo_downloader.download_template.return_value = 'repo_path'

        template_compiler = Mock()

        standards = Mock()
        standards.fetch.return_value = {}

        command_executor = NewCommandExecutor(template_retriever=template_retriever,
                                              repository_downloader=repo_downloader,
                                              standards=standards,
                                              template_compiler=template_compiler)
        command_executor._get_template_params = Mock(return_value={})

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

    @patch("shellfoundry.commands.new_command.NewCommandExecutor._verify_template_standards_compatibility")
    def test_can_generate_shell_from_local_template(self, verification):
        # Arrange
        template_retriever = Mock()
        template_retriever.get_templates = Mock(return_value={'base': [ShellTemplate('base', '', 'url', '7.0')]})

        repo_downloader = Mock()
        repo_downloader.download_template.return_value = 'repo_path'

        template_compiler = Mock()

        standards = Mock()
        standards.fetch.return_value = {}

        command_executor = NewCommandExecutor(template_retriever=template_retriever,
                                              repository_downloader=repo_downloader,
                                              standards=standards,
                                              template_compiler=template_compiler)
        command_executor._get_template_params = Mock(return_value={})

        local_template = self.fs.CreateDirectory('shell_template_root').name

        # Act
        command_executor.new('new_shell', 'local:{template_dir}'.format(template_dir=local_template), 'master')

        template_compiler.compile_template.smarter_assert_called_once_with(
            CookiecutterTemplateCompiler.compile_template,
            shell_name='new_shell',
            template_path='shell_template_root',
            extra_context={},
            running_on_same_folder=False)

    @patch("shellfoundry.commands.new_command.NewCommandExecutor._verify_template_standards_compatibility")
    @httpretty.activate
    def test_integration_can_generate_shell_from_specific_version(self, verification):
        # Arrange
        templates = {'tosca/resource/test': [ShellTemplate('test-resource', '', 'url/test', '8.1', 'resource')]}
        repo_info = ('quali', 'resource-test')

        zipfile = mock_template_zip_file()
        httpretty.register_uri(httpretty.GET, "https://api.github.com/repos/quali/resource-test/zipball/1.1",
                               body=zipfile.read(), content_type='application/zip',
                               content_disposition="attachment; filename=quali-resource-test-dd2ba19.zip", stream=True)
        template_compiler = Mock()

        standards = Mock()
        standards.fetch.return_value = {"resource": ['1.0.0', '1.0.1']}

        template_versions = ['master', '1.0.0', '1.0.1']

        # Act
        with patch.object(TemplateRetriever, 'get_templates', return_value=templates), \
             patch('shellfoundry.utilities.template_url._parse_repo_url', return_value=repo_info), \
             patch.object(TempDirContext, '__enter__', return_value=self.fs.CreateDirectory('mock_temp').name):
            command_executor = NewCommandExecutor(template_retriever=TemplateRetriever(),
                                                  repository_downloader=RepositoryDownloader(),
                                                  template_compiler=template_compiler,
                                                  standards=standards,
                                                  standard_versions=StandardVersionsFactory())
            command_executor._get_template_params = Mock(return_value={})
            command_executor.new('new_shell', 'tosca/resource/test', '1.1')

        # Assert
            template_compiler.compile_template.smarter_assert_called_once_with(
                CookiecutterTemplateCompiler.compile_template,
                shell_name='new_shell',
                template_path=os.path.join('mock_temp', 'root'),
                extra_context={},
                running_on_same_folder=False)

    @patch("shellfoundry.commands.new_command.NewCommandExecutor._verify_template_standards_compatibility")
    @httpretty.activate
    def test_integration_can_generate_gen1_shell_from_specific_version(self, verification):
        # Arrange
        templates = {'tosca/resource/test': [ShellTemplate('test-resource', '', 'url/test', '8.1', 'resource')],
                     'gen1/resource': [ShellTemplate('gen1/resource', '', 'gen1/test', '7.0')]}
        repo_info = ('quali', 'resource-test')

        zipfile = mock_template_zip_file()
        httpretty.register_uri(httpretty.GET, "https://api.github.com/repos/quali/resource-test/zipball",
                               body=zipfile.read(), content_type='application/zip',
                               content_disposition="attachment; filename=quali-resource-test-dd2ba19.zip", stream=True)
        template_compiler = Mock()

        standards = Mock()
        standards.fetch.return_value = {"resource": ['1.0.0', '1.0.1']}

        # Act
        with patch.object(TemplateRetriever, 'get_templates', return_value=templates), \
             patch('shellfoundry.utilities.template_url._parse_repo_url', return_value=repo_info), \
             patch.object(TempDirContext, '__enter__', return_value=self.fs.CreateDirectory('mock_temp').name):
            command_executor = NewCommandExecutor(template_retriever=TemplateRetriever(),
                                                  repository_downloader=RepositoryDownloader(),
                                                  template_compiler=template_compiler,
                                                  standards=standards,
                                                  standard_versions=StandardVersionsFactory())
            command_executor._get_template_params = Mock(return_value={})
            command_executor.new('new_shell', 'gen1/resource')

        # Assert
        template_compiler.compile_template.smarter_assert_called_once_with(
            CookiecutterTemplateCompiler.compile_template,
            shell_name='new_shell',
            template_path=os.path.join('mock_temp', 'root'),
            extra_context={},
            running_on_same_folder=False)

    @patch("shellfoundry.commands.new_command.NewCommandExecutor._verify_template_standards_compatibility")
    @httpretty.activate
    def test_fail_to_generate_shell_when_requested_version_does_not_exists(self, verification):
        # Arrange
        templates = {'tosca/resource/test': [ShellTemplate('test-resource', '', 'url/test', '8.1', 'resource')]}
        repo_info = ('quali', 'resource-test')

        httpretty.register_uri(httpretty.GET, "https://api.github.com/repos/quali/resource-test/zipball/1.1",
                               body='', status=404, stream=True)
        template_compiler = Mock()

        standards = Mock()
        standards.fetch.return_value = {"resource": ['1.0.0', '1.0.1']}

        template_versions = ['master', '1.0.0', '1.0.1']

        # Act
        with patch.object(TemplateRetriever, 'get_templates', return_value=templates), \
             patch('shellfoundry.utilities.template_url._parse_repo_url', return_value=repo_info), \
             patch.object(TempDirContext, '__enter__', return_value=self.fs.CreateDirectory('mock_temp').name), \
             patch.object(TemplateVersions, 'get_versions_of_template', return_value=template_versions), \
             self.assertRaises(BadParameter) as context:
            command_executor = NewCommandExecutor(template_retriever=TemplateRetriever(),
                                                  repository_downloader=RepositoryDownloader(),
                                                  template_compiler=template_compiler,
                                                  standards=standards,
                                                  standard_versions=StandardVersionsFactory())
            command_executor._get_template_params = Mock(return_value={})
            command_executor.new('new_shell', 'tosca/resource/test', '1.1')

        # Assert
        self.assertTrue('Requested standard version (\'1.1\') does not match template version. \n'
                        'Available versions for test-resource: 1.0.0, 1.0.1' in context.exception,
                        'Actual: {}'.format(context.exception))

    @patch("shellfoundry.commands.new_command.NewCommandExecutor._verify_template_standards_compatibility")
    @httpretty.activate
    def test_integration_latest_version_is_default_when_version_was_not_specified(self, verification):
        # Arrange
        templates = {'tosca/resource/test': [ShellTemplate('test-resource', '', 'url', '8.1', 'resource')]}
        repo_info = ('quali', 'resource-test')

        zipfile = mock_template_zip_file()
        httpretty.register_uri(httpretty.GET, "https://api.github.com/repos/quali/resource-test/zipball/2.0.1",
                               body=zipfile.read(), content_type='application/zip',
                               content_disposition="attachment; filename=quali-resource-test-dd2ba19.zip", stream=True)
        template_compiler = Mock()

        standards = Mock()
        standards.fetch.return_value = {"resource": ['2.0.0', '2.0.1']}

        # Act
        with patch.object(TemplateRetriever, 'get_templates', return_value=templates), \
             patch('shellfoundry.utilities.template_url._parse_repo_url', return_value=repo_info), \
             patch.object(TempDirContext, '__enter__', return_value=self.fs.CreateDirectory('mock_temp').name):
            command_executor = NewCommandExecutor(template_retriever=TemplateRetriever(),
                                                  repository_downloader=RepositoryDownloader(),
                                                  template_compiler=template_compiler,
                                                  standards=standards,
                                                  standard_versions=StandardVersionsFactory())
            command_executor._get_template_params = Mock(return_value={})
            command_executor.new('new_shell', 'tosca/resource/test')

        # Assert
        template_compiler.compile_template.smarter_assert_called_once_with(
            CookiecutterTemplateCompiler.compile_template,
            shell_name='new_shell',
            template_path=os.path.join('mock_temp', 'root'),
            extra_context={},
            running_on_same_folder=False)

    @patch("shellfoundry.commands.new_command.NewCommandExecutor._verify_template_standards_compatibility")
    @httpretty.activate
    def test_new_cmd_creates_gen2_in_latest_version_that_matches_the_standard_version_on_cs(self, verification):
        # Arrange
        templates = """templates:
    - name : gen1/resource
      description : 1st generation shell template for basic inventory resources
      repository : https://github.com/QualiSystems/shell-resource-standard
      params:
        project_name :
      min_cs_ver: 7.0
    - name : gen2/networking/switch
      params:
        project_name :
        family_name: Switch
      description : 2nd generation shell template for a standard switch
      repository : https://github.com/QualiSystems/shellfoundry-tosca-networking-template
      min_cs_ver: 8.0"""

        template_compiler = Mock()

        standards = Mock()
        standards.fetch.return_value = {"networking": ['5.0.0', '5.0.1']}

        zipfile = mock_template_zip_file()

        httpretty.register_uri(httpretty.GET, TEMPLATES_YML, body=templates)
        httpretty.register_uri(httpretty.GET,
                               "https://api.github.com/repos/QualiSystems/shellfoundry-tosca-networking-template/zipball/5.0.1",
                               body=zipfile.read(), content_type='application/zip',
                               content_disposition="attachment; filename=quali-resource-test-dd2ba19.zip", stream=True)

        # Act
        with \
                patch.object(TemplateRetriever, '_get_templates_from_github', return_value=templates), \
                patch.object(TempDirContext, '__enter__', return_value=self.fs.CreateDirectory('mock_temp').name):
            cmd = NewCommandExecutor(template_retriever=TemplateRetriever(),
                                     repository_downloader=RepositoryDownloader(),
                                     template_compiler=template_compiler, standards=standards,
                                     standard_versions=StandardVersionsFactory())
            cmd.new('new_shell', 'gen2/networking/switch')

            # Assert
            template_compiler.compile_template.smarter_assert_called_once_with(
                CookiecutterTemplateCompiler.compile_template,
                shell_name='new_shell',
                template_path=os.path.join('mock_temp', 'root'),
                extra_context={'family_name': "Switch", "project_name": None},
                running_on_same_folder=False)

    # @patch("shellfoundry.commands.new_command.NewCommandExecutor._verify_template_standards_compatibility")
    # @httpretty.activate
    # def test_new_cmd_creates_gen2_when_get_cs_standards_feature_is_unavailable(self, verification):
    #     # Arrange
    #     self.fs.add_real_file(ALTERNATIVE_STANDARDS_PATH)
    #     self.fs.add_real_file(ALTERNATIVE_TEMPLATES_PATH)
    #
    #     template_compiler = Mock()
    #     zipfile = mock_template_zip_file()
    #
    #     httpretty.register_uri(httpretty.GET,
    #                            "https://api.github.com/repos/QualiSystems/shellfoundry-tosca-networking-template/zipball/5.0.0",
    #                            body=zipfile.read(), content_type='application/zip',
    #                            content_disposition="attachment; filename=quali-resource-test-dd2ba19.zip", stream=True)
    #
    #     # Act
    #     with \
    #             patch.object(Standards, '_fetch_from_cloudshell', side_effect=FeatureUnavailable()), \
    #             patch.object(TempDirContext, '__enter__', return_value=self.fs.CreateDirectory('mock_temp').name):
    #         cmd = NewCommandExecutor(template_retriever=TemplateRetriever(),
    #                                  repository_downloader=RepositoryDownloader(),
    #                                  template_compiler=template_compiler, standards=Standards(),
    #                                  standard_versions=StandardVersionsFactory())
    #         cmd.new('new_shell', 'gen2/networking/switch')
    #
    #         # Assert
    #         template_compiler.compile_template.smarter_assert_called_once_with(
    #             CookiecutterTemplateCompiler.compile_template,
    #             shell_name='new_shell',
    #             template_path=os.path.join('mock_temp', 'root'),
    #             extra_context={'family_name': "Switch", "project_name": None},
    #             running_on_same_folder=False)
    #
    # @patch("shellfoundry.commands.new_command.NewCommandExecutor._verify_template_standards_compatibility")
    # @httpretty.activate
    # def test_requested_template_does_not_exists_raises_an_error(self, verification):
    #     # Arrange
    #     self.fs.add_real_file(ALTERNATIVE_STANDARDS_PATH)
    #     self.fs.add_real_file(ALTERNATIVE_TEMPLATES_PATH)
    #
    #     template_compiler = Mock()
    #     zipfile = mock_template_zip_file()
    #
    #     httpretty.register_uri(httpretty.GET,
    #                            "https://api.github.com/repos/QualiSystems/shellfoundry-tosca-networking-template/zipball/5.0.0",
    #                            body=zipfile.read(), content_type='application/zip',
    #                            content_disposition="attachment; filename=quali-resource-test-dd2ba19.zip", stream=True)
    #
    #     # Act
    #     with \
    #             patch.object(Standards, '_fetch_from_cloudshell', side_effect=FeatureUnavailable()), \
    #             patch.object(TempDirContext, '__enter__', return_value=self.fs.CreateDirectory('mock_temp').name):
    #         cmd = NewCommandExecutor(template_retriever=TemplateRetriever(),
    #                                  repository_downloader=RepositoryDownloader(),
    #                                  template_compiler=template_compiler, standards=Standards(),
    #                                  standard_versions=StandardVersionsFactory())
    #         # Assert
    #         output_msg = "Template gen2/doesnot/exists does not exist. Supported templates are: gen1/resource, " \
    #                      "gen1/resource-clean, gen1/deployed-app, gen1/networking/switch, gen1/networking/router," \
    #                      " gen1/pdu, gen1/firewall, gen1/compute, layer-1-switch, gen2/networking/switch, " \
    #                      "gen2/networking/router, gen2/networking/wireless-controller, gen2/compute, " \
    #                      "gen2/deployed-app, gen2/pdu, gen2/resource, gen2/firewall"
    #         self.assertRaisesRegexp(BadParameter, output_msg, cmd.new, 'new_shell', 'gen2/doesnot/exists')

    def test_new_command_with_invalid_shell_name_raises_bad_parameter_error(self):
        # Arrange
        shell_name = '15vido'

        # Act
        cmd = NewCommandExecutor()

        # Assert
        output_msg = u"Shell name must begin with a letter and contain only alpha-numeric characters and spaces."
        self.assertRaisesRegexp(BadParameter, output_msg, cmd.new, shell_name, 'gen2/resource')
