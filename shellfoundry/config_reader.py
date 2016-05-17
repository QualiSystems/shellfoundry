import os

import yaml

INSTALL = 'install'

DEFAULT_HOST = 'localhost'
DEFAULT_PORT = 9000
DEFAULT_USERNAME = 'admin'
DEFAULT_PASSWORD = 'admin'
DEFAULT_DOMAIN = 'Global'

HOST = 'host'
PORT = 'port'
USERNAME = 'username'
PASSWORD = 'password'
DOMAIN = 'domain'


class Config(object):
    def __init__(self, host, port, username, password, domain):
        self.domain = domain
        self.password = password
        self.username = username
        self.port = port
        self.host = host


class ConfigReader(object):
    def read(self, config_path=None):
        config_path = config_path or os.path.join(os.getcwd(), 'shellfoundry.yml')

        if not os.path.isfile(config_path):
            return Config(DEFAULT_HOST, DEFAULT_PORT, DEFAULT_USERNAME, DEFAULT_PASSWORD, DEFAULT_DOMAIN)

        with open(config_path) as stream:
            config = yaml.load(stream.read())

        if not config or INSTALL not in config:
            return Config(DEFAULT_HOST, DEFAULT_PORT, DEFAULT_USERNAME, DEFAULT_PASSWORD, DEFAULT_DOMAIN)

        install_config = config[INSTALL]

        host = self._get_with_default(install_config, HOST, DEFAULT_HOST)
        port = self._get_with_default(install_config, PORT, DEFAULT_PORT)
        username = self._get_with_default(install_config, USERNAME, DEFAULT_USERNAME)
        password = self._get_with_default(install_config, PASSWORD, DEFAULT_PASSWORD)
        domain = self._get_with_default(install_config, DOMAIN, DEFAULT_DOMAIN)

        return Config(host, port, username, password, domain)

    @staticmethod
    def _get_with_default(install_config, parameter_name, default_value):
        return install_config[parameter_name] if install_config and parameter_name in install_config else default_value
