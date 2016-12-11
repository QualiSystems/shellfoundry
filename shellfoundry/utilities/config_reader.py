import os
import yaml

from shellfoundry.models.install_config import InstallConfig, DEFAULT_HOST, DEFAULT_PORT, DEFAULT_USERNAME, \
    DEFAULT_PASSWORD, DEFAULT_DOMAIN
from shellfoundry.models.shellfoundry_settings import ShellFoundrySettings, DEFAULT_DEFAULT_VIEW
from shellfoundry.utilities.config.config_providers import DefaultConfigProvider

INSTALL = 'install'

HOST = 'host'
PORT = 'port'
USERNAME = 'username'
PASSWORD = 'password'
DOMAIN = 'domain'

DEFAULT_VIEW = 'defaultview'


def get_with_default(install_config, parameter_name, default_value):
    '''

    :param install_config: A dict represents the install section inside the configuration file
    :param parameter_name: Specific key inside the install section
    :param default_value: Default value in cases that the key cannot be found
    :return: The value of the key in the configuration file or default value if key cannot be found
    '''
    return install_config[parameter_name] if install_config and parameter_name in install_config else default_value


class Configuration(object):
    def __init__(self, reader, config_provider=None):
        self.reader = reader
        self.config_provider = config_provider or DefaultConfigProvider()

    def read(self):
        config_path = self.config_provider.get_config_path()

        if config_path is None or not os.path.isfile(config_path):
            return self.reader.get_defaults()

        with open(config_path) as stream:
            config = yaml.load(stream.read())

        if not config or INSTALL not in config:
            return self.reader.get_defaults()

        return self.reader.read_from_config(config[INSTALL])


class CloudShellConfigReader(object):
    def get_defaults(self):
        return InstallConfig.get_default()

    def read_from_config(self, config):
        host = get_with_default(config, HOST, DEFAULT_HOST)
        port = get_with_default(config, PORT, DEFAULT_PORT)
        username = get_with_default(config, USERNAME, DEFAULT_USERNAME)
        password = get_with_default(config, PASSWORD, DEFAULT_PASSWORD)
        domain = get_with_default(config, DOMAIN, DEFAULT_DOMAIN)
        return InstallConfig(host, port, username, password, domain)


class ShellFoundryConfig(object):
    def get_defaults(self):
        return ShellFoundrySettings.get_default()

    def read_from_config(self, config):
        defaultview = get_with_default(config, DEFAULT_VIEW, DEFAULT_DEFAULT_VIEW)
        return ShellFoundrySettings(defaultview)
