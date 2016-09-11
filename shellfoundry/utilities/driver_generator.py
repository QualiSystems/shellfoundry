import urllib2
import zipfile
import click
from os import path
from requests import post
from cloudshell.rest.api import PackagingRestApiClient
from shellfoundry.utilities.temp_dir_context import TempDirContext
from shellfoundry.models.install_config import InstallConfig


class DriverGenerator(object):
    def generate_driver(self, cloudshell_config, destination_path, package_full_path, shell_filename, shell_package):
        """

        :param cloudshell_config:
        :type cloudshell_config: InstallConfig
        :param destination_path:
        :param package_full_path:
        :param shell_filename:
        :param shell_package:
        :return:
        """
        client = DriverGenerator._connect_to_cloudshell(cloudshell_config)
        DriverGenerator._generate_driver_data_model(client, cloudshell_config, destination_path, package_full_path,
                                                    shell_filename,
                                                    shell_package)

    @staticmethod
    def _generate_driver_data_model(client, cloudshell_config, destination_path, package_full_path,
                                    shell_filename, shell_package):
        """

        :param client:
        :param cloudshell_config:
        :type cloudshell_config: InstallConfig
        :param destination_path:
        :param package_full_path:
        :param shell_filename:
        :param shell_package:
        :return:
        """
        url = 'http://{0}:{1}/API/ShellDrivers/Generate'.format(cloudshell_config.host, cloudshell_config.port)
        token = client.token
        response = post(url,
                        files={path.basename(shell_filename): open(package_full_path, 'rb')},
                        headers={'Authorization': 'Basic ' + token})
        click.echo('Extracting data model ...')
        with TempDirContext(shell_package.get_shell_name()) as temp_dir:
            generated_zip = path.join(temp_dir, shell_filename)
            with open(generated_zip, 'wb') as driver_file:
                driver_file.write(response.content)

            with zipfile.ZipFile(generated_zip) as zf:
                zf.extractall(destination_path)

    @staticmethod
    def _connect_to_cloudshell(cloudshell_config):
        try:
            client = PackagingRestApiClient(ip=cloudshell_config.host,
                                            username=cloudshell_config.username,
                                            port=cloudshell_config.port,
                                            domain=cloudshell_config.domain,
                                            password=cloudshell_config.password)
            return client
        except urllib2.URLError:
            click.echo(u'Login to CloudShell failed. Please verify the credentials in cloudshell_config.yml', err=True)
            raise
