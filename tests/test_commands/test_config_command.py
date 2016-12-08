from mock import patch, call
from pyfakefs import fake_filesystem_unittest

from shellfoundry.commands.config_command import ConfigCommandExecutor


class TestConfigCommandExecutor(fake_filesystem_unittest.TestCase):
    def setUp(self):
        self.setUpPyfakefs()

    @patch('shellfoundry.utilities.config.config_providers.click.get_app_dir')
    @patch('shellfoundry.commands.config_command.click.echo')
    def test_get_all_config_keys(self, echo_mock, get_app_dir_mock):
        # Arrange
        self.fs.CreateFile('/quali/shellfoundry/global_config.yml', contents="""
install:
  key: value
not_supported_section:
  no_key: no_value
    """)
        get_app_dir_mock.return_value = '/quali/shellfoundry'

        # Act
        ConfigCommandExecutor(True).config()

        # Assert
        echo_mock.assert_called_once_with(u'key: value')

    @patch('shellfoundry.utilities.config.config_providers.click.get_app_dir')
    @patch('shellfoundry.commands.config_command.click.echo')
    def test_invalid_global_config_should_echo_no_install_section(self, echo_mock, get_app_dir_mock):
        # Arrange
        self.fs.CreateFile('/quali/shellfoundry/global_config.yml', contents="""
invalid_section:
  key: value
        """)
        get_app_dir_mock.return_value = '/quali/shellfoundry'

        # Act
        ConfigCommandExecutor(True).config()

        # Assert
        # calls = [call(u'username: admin'),
        #          call(u'domain: Global'),
        #          call(u'password: [encrypted]'),
        #          call(u'host: localhost'),
        #          call(u'port: 9000')]
        # click_mock.echo.assert_has_calls(calls)
        echo_mock.assert_called_once_with('Global config file has no \'install\' section.')

    @patch('shellfoundry.utilities.config.config_providers.click.get_app_dir')
    @patch('shellfoundry.commands.config_command.click.echo')
    def test_set_global_config_key(self, echo_mock, get_app_dir_mock):
        # Arrange
        self.fs.CreateFile('/quali/shellfoundry/global_config.yml', contents="""
install:
  key: value""")
        get_app_dir_mock.return_value = '/quali/shellfoundry'

        # Act
        ConfigCommandExecutor(True).config(('new_key', 'new_value'))

        # Assert
        echo_mock.assert_called_once_with('new_key: new_value was saved successfully')
        desired_result = """install:
  key: value
  new_key: new_value
"""
        self.assertTrue(self.fs.GetObject('/quali/shellfoundry/global_config.yml').contents == desired_result)

    @patch('shellfoundry.utilities.config.config_providers.os.getcwd')
    @patch('shellfoundry.commands.config_command.click.echo')
    def test_set_local_config_key(self, echo_mock, getcwd_mock):
        # Arrange
        self.fs.CreateFile('/current_shell/cloudshell_config.yml', contents="""
install:
  key: value""")
        getcwd_mock.return_value = '/current_shell'
        # Act
        ConfigCommandExecutor(False).config(('new_key', 'new_value'))

        # Assert
        echo_mock.assert_called_once_with('new_key: new_value was saved successfully')
        desired_result = """install:
  key: value
  new_key: new_value
"""
        self.assertTrue(self.fs.GetObject('/current_shell/cloudshell_config.yml').contents == desired_result)

    @patch('shellfoundry.utilities.config.config_providers.click.get_app_dir')
    @patch('shellfoundry.commands.config_command.click.echo')
    def test_get_all_config_keys_that_has_password_param(self, echo_mock, get_app_dir_mock):
        # Arrange
        self.fs.CreateFile('/quali/shellfoundry/global_config.yml', contents="""
install:
  key: value
  password: aabcdefs
  yetanotherkey: yetanothervalue""")
        get_app_dir_mock.return_value = '/quali/shellfoundry'

        # Act
        ConfigCommandExecutor(True).config()

        # Assert
        calls = [call(u'yetanotherkey: yetanothervalue'),
                 call(u'password: [encrypted]'),
                 call(u'key: value')]
        echo_mock.assert_has_calls(calls)

    @patch('shellfoundry.utilities.config.config_providers.click.get_app_dir')
    @patch('shellfoundry.commands.config_command.click.echo')
    def test_remove_key_is_allowed(self, echo_mock, get_app_dir_mock):
        # Arrange
        self.fs.CreateFile('/quali/shellfoundry/global_config.yml', contents="""
install:
  key: value
  yetanotherkey: yetanothervalue""")
        get_app_dir_mock.return_value = '/quali/shellfoundry'
        key = 'yetanotherkey'

        # Act
        ConfigCommandExecutor(True).config(key_to_remove=key)

        # Assert
        echo_mock.assert_called_once_with('yetanotherkey was deleted successfully')
        desired_result = """install:
  key: value
"""
        file_content = self.fs.GetObject('/quali/shellfoundry/global_config.yml').contents
        import os
        self.assertTrue(file_content == desired_result, 'Expected: {}{}Actual: {}'
                        .format(desired_result, os.linesep, file_content))

    @patch('shellfoundry.utilities.config.config_providers.click.get_app_dir')
    @patch('shellfoundry.commands.config_command.click.echo')
    def test_update_existing_key(self, echo_mock, get_app_dir_mock):
        # Arrange
        self.fs.CreateFile('/quali/shellfoundry/global_config.yml', contents="""
install:
  key: value""")
        get_app_dir_mock.return_value = '/quali/shellfoundry'

        # Act
        ConfigCommandExecutor(True).config(('key', 'new_value'))

        # Assert
        echo_mock.assert_called_once_with('key: new_value was saved successfully')
        desired_result = """install:
  key: new_value
"""
        file_content = self.fs.GetObject('/quali/shellfoundry/global_config.yml').contents
        import os
        self.assertTrue(file_content == desired_result, 'Expected: {}{}Actual: {}'
                        .format(desired_result, os.linesep, file_content))

    @patch('shellfoundry.utilities.config.config_providers.click.get_app_dir')
    @patch('shellfoundry.commands.config_command.click.echo')
    def test_adding_key_to_global_config_that_hasnt_been_created_yet(self, echo_mock, get_app_dir_mock):
        # Arrange
        get_app_dir_mock.return_value = '/quali/shellfoundry'

        # Act
        ConfigCommandExecutor(True).config(('key', 'new_value'))

        # Assert
        echo_mock.assert_called_with('key: new_value was saved successfully')
        desired_result = """install:
  key: new_value
"""
        file_content = self.fs.GetObject('/quali/shellfoundry/global_config.yml').contents
        import os
        self.assertTrue(file_content == desired_result, 'Expected: {}{}Actual: {}'
                        .format(desired_result, os.linesep, file_content))
