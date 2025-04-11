from __future__ import annotations

import json
import os
import time
from typing import TYPE_CHECKING, ClassVar
from urllib.error import HTTPError

import click
from attrs import define, field
from cloudshell.rest.api import PackagingRestApiClient
from cloudshell.rest.exceptions import FeatureUnavailable, ShellNotFound

from shellfoundry.constants import (
    CLOUDSHELL_MAX_RETRIES,
    CLOUDSHELL_RETRY_INTERVAL_SEC,
    DEFAULT_TIME_WAIT,
)
from shellfoundry.exceptions import FatalError
from shellfoundry.utilities.config_reader import CloudShellConfigReader, Configuration
from shellfoundry.utilities.shell_package import ShellPackage

if TYPE_CHECKING:
    from click._termui_impl import ProgressBar

    from shellfoundry.models.install_config import InstallConfig


SHELL_IS_OFFICIAL_FLAG = "IsOfficial"


@define
class ShellPackageInstaller:
    GLOBAL_DOMAIN: ClassVar[str] = "Global"
    cloudshell_config_reader: Configuration = field(
        factory=lambda: Configuration(CloudShellConfigReader())
    )

    def install(self, path: str) -> None:
        """Install new or Update existed Shell."""
        shell_package = ShellPackage(path)
        shell_name = shell_package.get_name_from_definition()
        shell_filename = f"{shell_name}.zip"
        package_full_path = os.path.join(path, "dist", shell_filename)

        cloudshell_config = self.cloudshell_config_reader.read()

        if cloudshell_config.domain != self.GLOBAL_DOMAIN:
            raise click.UsageError(
                "Gen2 shells could not be installed into non Global domain."
            )

        cs_connection_label = f"Connecting to CloudShell at {cloudshell_config.host}:{cloudshell_config.port}"  # noqa: E501
        with click.progressbar(
            length=CLOUDSHELL_MAX_RETRIES, show_eta=False, label=cs_connection_label
        ) as pbar:
            try:
                client = self._open_connection_to_quali_server(
                    cloudshell_config, pbar, retry=CLOUDSHELL_MAX_RETRIES
                )
            finally:
                self._render_pbar_finish(pbar)

        try:
            is_official = client.get_shell(shell_name=shell_name).get(
                SHELL_IS_OFFICIAL_FLAG, False
            )

            if is_official:
                click.confirm(
                    text="Upgrading to a custom version of the shell will limit you "
                    "only to customized versions of this shell from now on. "
                    "You won't be able to upgrade it to an official version of the shell in the future."  # noqa: E501
                    "\nDo you wish to continue?",
                    abort=True,
                )
        except FeatureUnavailable:
            # try to update shell first
            pass
        except ShellNotFound:
            # try to install shell
            pass
        except click.Abort:
            raise
        except Exception as e:
            raise FatalError(
                self._parse_installation_error(
                    "Failed to get information about installed shell", e
                )
            )

        pbar_install_shell_len = 2  # amount of possible actions (update and add)
        installation_label = "Installing shell into CloudShell".ljust(
            len(cs_connection_label)
        )
        with click.progressbar(
            length=pbar_install_shell_len, show_eta=False, label=installation_label
        ) as pbar:
            try:
                client.update_shell(package_full_path)
            except ShellNotFound:
                self._increase_pbar(pbar, DEFAULT_TIME_WAIT)
                self._add_new_shell(client, package_full_path)
            except Exception as e:
                self._increase_pbar(pbar, DEFAULT_TIME_WAIT)
                raise FatalError(
                    self._parse_installation_error("Failed to update shell", e)
                )
            finally:
                self._render_pbar_finish(pbar)

    def delete(self, shell_name: str) -> None:
        """Delete Shell."""
        cloudshell_config = self.cloudshell_config_reader.read()

        if cloudshell_config.domain != self.GLOBAL_DOMAIN:
            raise click.UsageError(
                "Gen2 shells could not be deleted from non Global domain."
            )

        cs_connection_label = f"Connecting to CloudShell at {cloudshell_config.host}:{cloudshell_config.port}"  # noqa: E501
        with click.progressbar(
            length=CLOUDSHELL_MAX_RETRIES, show_eta=False, label=cs_connection_label
        ) as pbar:
            try:
                client = self._open_connection_to_quali_server(
                    cloudshell_config, pbar, retry=CLOUDSHELL_MAX_RETRIES
                )
            finally:
                self._render_pbar_finish(pbar)

        pbar_install_shell_len = 2  # amount of possible actions (update and add)
        installation_label = "Deleting shell from CloudShell".ljust(
            len(cs_connection_label)
        )
        with click.progressbar(
            length=pbar_install_shell_len, show_eta=False, label=installation_label
        ) as pbar:
            try:
                client.delete_shell(shell_name)
            except FeatureUnavailable:
                self._increase_pbar(pbar, DEFAULT_TIME_WAIT)
                raise click.ClickException(
                    "Delete shell command unavailable (probably due to CloudShell version below 9.2)"  # noqa: E501
                )
            except ShellNotFound:
                self._increase_pbar(pbar, DEFAULT_TIME_WAIT)
                raise click.ClickException(
                    f"Shell '{shell_name}' doesn't exist on CloudShell"
                )
            except Exception as e:
                self._increase_pbar(pbar, DEFAULT_TIME_WAIT)
                raise click.ClickException(
                    self._parse_installation_error("Failed to delete shell", e)
                )
            finally:
                self._render_pbar_finish(pbar)

    def _open_connection_to_quali_server(
        self, cloudshell_config: InstallConfig, pbar: ProgressBar, retry: int
    ) -> PackagingRestApiClient:
        if retry == 0:
            raise FatalError(
                "Connection to CloudShell Server failed. "
                "Please make sure it is up and running properly."
            )
        try:
            client = PackagingRestApiClient.login(
                host=cloudshell_config.host,
                port=cloudshell_config.port,
                username=cloudshell_config.username,
                password=cloudshell_config.password,
                domain=cloudshell_config.domain,
            )
            return client
        except HTTPError as e:
            if e.code == 401:
                raise FatalError(
                    "Login to CloudShell failed. "
                    "Please verify the credentials in the config"
                )
            raise FatalError(
                "Connection to CloudShell Server failed. "
                "Please make sure it is up and running properly."
            )
        except Exception:
            self._increase_pbar(pbar, time_wait=CLOUDSHELL_RETRY_INTERVAL_SEC)
            return self._open_connection_to_quali_server(
                cloudshell_config, pbar, retry - 1
            )

    def _add_new_shell(
        self, client: PackagingRestApiClient, package_full_path: str
    ) -> None:
        """Try to add new Shell to Cloudshell."""
        try:
            client.add_shell(package_full_path)
        except Exception as e:
            raise FatalError(
                self._parse_installation_error("Failed to add new shell", e)
            )

    @staticmethod
    def _parse_installation_error(base_message: str, error: Exception) -> str:
        try:
            cs_message = json.loads(str(error))["Message"]
        except Exception:
            cs_message = ""
        return f"{base_message}. CloudShell responded with: '{cs_message}'"

    @staticmethod
    def _increase_pbar(pbar: ProgressBar, time_wait: int | float) -> None:
        time.sleep(time_wait)
        pbar.make_step(1)

    @staticmethod
    def _render_pbar_finish(pbar: ProgressBar) -> None:
        pbar.finish()
        pbar.render_progress()
