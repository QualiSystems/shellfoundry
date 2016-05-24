import os
import yaml

from shellfoundry.models.install_config import InstallConfig, DEFAULT_HOST, DEFAULT_PORT, DEFAULT_USERNAME, \
    DEFAULT_PASSWORD, DEFAULT_DOMAIN

INSTALL = 'install'

HOST = 'host'
PORT = 'port'
USERNAME = 'username'
PASSWORD = 'password'
DOMAIN = 'domain'


class CloudShellConfigReader(object):
    def read(self):
        """

        :return:
        :rtype shellfoundry.models.install_config.Installconfig
        """
        config_path = os.path.join(os.getcwd(), 'cloudshell_config.yml')

        if not os.path.isfile(config_path):
            return InstallConfig.get_default()

        with open(config_path) as stream:
            config = yaml.load(stream.read())

        if not config or INSTALL not in config:
            return InstallConfig.get_default()

        install_config = config[INSTALL]

        host = self._get_with_default(install_config, HOST, DEFAULT_HOST)
        port = self._get_with_default(install_config, PORT, DEFAULT_PORT)
        username = self._get_with_default(install_config, USERNAME, DEFAULT_USERNAME)
        password = self._get_with_default(install_config, PASSWORD, DEFAULT_PASSWORD)
        domain = self._get_with_default(install_config, DOMAIN, DEFAULT_DOMAIN)

        return InstallConfig(host, port, username, password, domain)

    @staticmethod
    def _get_with_default(install_config, parameter_name, default_value):
        return install_config[parameter_name] if install_config and parameter_name in install_config else default_value


