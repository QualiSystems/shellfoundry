#!/usr/bin/python
# -*- coding: utf-8 -*-

import click
import os
import time
import json

from urllib2 import HTTPError

from shellfoundry.exceptions import FatalError
from shellfoundry.utilities.config_reader import Configuration, CloudShellConfigReader
from shellfoundry.utilities.shell_package import ShellPackage
from cloudshell.rest.api import PackagingRestApiClient
from cloudshell.rest.exceptions import ShellNotFoundException, FeatureUnavailable
from shellfoundry.utilities.constants import CLOUDSHELL_MAX_RETRIES, CLOUDSHELL_RETRY_INTERVAL_SEC, DEFAULT_TIME_WAIT


SHELL_IS_OFFICIAL_FLAG = "IsOfficial"


class ShellPackageInstaller(object):
    GLOBAL_DOMAIN = 'Global'
    
    def __init__(self):
        self.cloudshell_config_reader = Configuration(CloudShellConfigReader())

    def install(self, path):
        shell_package = ShellPackage(path)
        # shell_name = shell_package.get_shell_name()
        shell_name = shell_package.get_name_from_definition()
        shell_filename = shell_name + ".zip"
        package_full_path = os.path.join(path, "dist", shell_filename)

        cloudshell_config = self.cloudshell_config_reader.read()

        if cloudshell_config.domain != self.GLOBAL_DOMAIN:
            raise click.UsageError("Gen2 shells could not be installed into non Global domain.")

        cs_connection_label = "Connecting to CloudShell at {}:{}".format(cloudshell_config.host, cloudshell_config.port)
        with click.progressbar(length=CLOUDSHELL_MAX_RETRIES,
                               show_eta=False,
                               label=cs_connection_label
                               ) as pbar:
            try:
                client = self._open_connection_to_quali_server(cloudshell_config, pbar, retry=CLOUDSHELL_MAX_RETRIES)
            finally:
                self._render_pbar_finish(pbar)

        try:
            is_official = client.get_shell(shell_name=shell_name).get(SHELL_IS_OFFICIAL_FLAG, False)

            if is_official:
                click.confirm(text="Upgrading to a custom version of the shell will limit you "
                                   "only to customized versions of this shell from now on. "
                                   "You won't be able to upgrade it to an official version of the shell in the future."
                                   "\nDo you wish to continue?",
                              abort=True)

        except FeatureUnavailable:
            # try to update shell first
            pass
        except ShellNotFoundException:
            # try to install shell
            pass
        except click.Abort:
            raise
        except Exception as e:
            raise FatalError(self._parse_installation_error("Failed to get information about installed shell", e))

        pbar_install_shell_len = 2  # amount of possible actions (update and add)
        installation_label = "Installing shell into CloudShell".ljust(len(cs_connection_label))
        with click.progressbar(length=pbar_install_shell_len,
                               show_eta=False,
                               label=installation_label) as pbar:
            try:
                client.update_shell(package_full_path)
            except ShellNotFoundException:
                self._increase_pbar(pbar, DEFAULT_TIME_WAIT)
                self._add_new_shell(client, package_full_path)
            except Exception as e:
                self._increase_pbar(pbar, DEFAULT_TIME_WAIT)
                raise FatalError(self._parse_installation_error("Failed to update shell", e))
            finally:
                self._render_pbar_finish(pbar)

    def _open_connection_to_quali_server(self, cloudshell_config, pbar, retry):
        if retry == 0:
            raise FatalError("Connection to CloudShell Server failed. Please make sure it is up and running properly.")

        try:
            client = PackagingRestApiClient(ip=cloudshell_config.host,
                                            username=cloudshell_config.username,
                                            port=cloudshell_config.port,
                                            domain=cloudshell_config.domain,
                                            password=cloudshell_config.password)
            return client
        except HTTPError as e:
            if e.code == 401:
                raise FatalError(u"Login to CloudShell failed. Please verify the credentials in the config")
            raise FatalError("Connection to CloudShell Server failed. Please make sure it is up and running properly.")
        except:
            self._increase_pbar(pbar, time_wait=CLOUDSHELL_RETRY_INTERVAL_SEC)
            return self._open_connection_to_quali_server(cloudshell_config, pbar, retry - 1)

    def _add_new_shell(self, client, package_full_path):
        try:
            client.add_shell(package_full_path)
        except Exception as e:
            raise FatalError(self._parse_installation_error("Failed to add new shell", e))

    def _parse_installation_error(self, base_message, error):
        cs_message = json.loads(error.message)["Message"]
        return "{}. CloudShell responded with: '{}'".format(base_message, cs_message)

    def _increase_pbar(self, pbar, time_wait):
        time.sleep(time_wait)
        pbar.next()

    def _render_pbar_finish(self, pbar):
        pbar.finish()
        pbar.render_progress()
