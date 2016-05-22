import os
from qpm.packaging.quali_api_client import QualiAPIClient


class ShellInstaller(object):
    def install(self, package_name, config):
        """

        :param package_name:
        :param config:
        :type config shellfoundry.config_reader.InstallConfig
        :return:
        """

        host = config.host
        port = config.port
        username = config.username
        password = config.password
        domain = config.domain

        print 'Installing package {0} into CloudShell at http://{1}:{2}'.format(package_name, host, port)
        server = QualiAPIClient(host, port, username, password, domain)
        server.upload_environment_zip_file(os.path.join(os.getcwd(), package_name + '.zip'))
