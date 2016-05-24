import os
import click
from qpm.packaging.quali_api_client import QualiAPIClient


class ShellInstaller(object):
    def install(self, package_name, config):
        """
        Installs package according to cloudshell
        :param package_name: Package name to install
        :type package_name str
        :param config: Configuration to be used for
        :type config shellfoundry.models.install_config.InstallConfig
        :return:
        """
        host = config.host
        port = config.port
        username = config.username
        password = config.password
        domain = config.domain

        package_full_path = os.path.join(os.getcwd(), 'dist', package_name + '.zip')
        click.echo('Installing package {0} into CloudShell at http://{1}:{2}'.format(package_full_path, host, port))
        server = QualiAPIClient(host, port, username, password, domain)
        server.upload_environment_zip_file(package_full_path)
