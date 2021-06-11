#!/usr/bin/python
# -*- coding: utf-8 -*-
try:
    from urllib.error import URLError
except ImportError:
    from urllib2 import URLError

import zipfile
from io import open
from os import path

import click
from cloudshell.rest.api import PackagingRestApiClient
from requests import post

from shellfoundry.utilities.temp_dir_context import TempDirContext


class DriverGenerator(object):
    def generate_driver(
        self,
        cloudshell_config,
        destination_path,
        package_full_path,
        shell_filename,
        shell_name,
    ):
        """Generates Python data model by connecting to Cloudshell server.

        :param cloudshell_config:
        :type cloudshell_config: InstallConfig
        :param destination_path:
        :param package_full_path:
        :param shell_filename:
        :param shell_name:
        :return:
        """
        client = self._connect_to_cloudshell(cloudshell_config)
        self._generate_driver_data_model(
            client=client,
            cloudshell_config=cloudshell_config,
            destination_path=destination_path,
            package_full_path=package_full_path,
            shell_filename=shell_filename,
            shell_name=shell_name,
        )

    @staticmethod
    def _generate_driver_data_model(
        client,
        cloudshell_config,
        destination_path,
        package_full_path,
        shell_filename,
        shell_name,
    ):
        """Generates driver data model.

        :param client:
        :param cloudshell_config:
        :type cloudshell_config: InstallConfig
        :param destination_path:
        :param package_full_path:
        :param shell_filename:
        :param shell_name:
        :return:
        """
        url = "http://{0}:{1}/API/ShellDrivers/Generate".format(
            cloudshell_config.host, cloudshell_config.port
        )
        token = client.token
        response = post(
            url,
            files={
                path.basename(shell_filename): open(
                    package_full_path, "rb", encoding="utf8"
                )
            },
            headers={"Authorization": "Basic " + token},
        )

        if response.status_code != 200:
            error_message = "Code generation failed with code {0} and error {1}".format(
                response.status_code, response.text
            )
            click.echo(message=error_message, err=True)
            return

        click.echo("Extracting data model ...")
        with TempDirContext(remove_dir_on_error=False, prefix=shell_name) as temp_dir:
            generated_zip = path.join(temp_dir, shell_filename)
            click.echo("Writing temporary file {0}".format(generated_zip))
            with open(generated_zip, "wb", encoding="utf8") as driver_file:
                driver_file.write(response.content)

            click.echo("Extracting generated code at {0}".format(destination_path))
            with zipfile.ZipFile(generated_zip) as zf:
                zf.extractall(destination_path)

    @staticmethod
    def _connect_to_cloudshell(cloudshell_config):
        try:
            client = PackagingRestApiClient(
                ip=cloudshell_config.host,
                username=cloudshell_config.username,
                port=cloudshell_config.port,
                domain=cloudshell_config.domain,
                password=cloudshell_config.password,
            )
            return client
        except URLError:
            click.echo(
                "Login to CloudShell failed. Please verify the credentials in cloudshell_config.yml",  # noqa: E501
                err=True,
            )
            raise
