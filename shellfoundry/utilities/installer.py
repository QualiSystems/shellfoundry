#!/usr/bin/python
# -*- coding: utf-8 -*-

import os

import click
from cloudshell.rest.api import PackagingRestApiClient


class ShellInstaller(object):
    def install(self, package_name, config):
        """Installs package according to cloudshell.

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

        package_full_path = os.path.join(os.getcwd(), "dist", package_name + ".zip")
        click.echo(
            "Installing package {0} into CloudShell at http://{1}:{2}".format(
                package_full_path, host, port
            )
        )
        server = PackagingRestApiClient(host, port, username, password, domain)
        server.import_package(package_full_path)
