from __future__ import annotations

import os
from typing import TYPE_CHECKING

import yaml
from attrs import asdict, define, field

from shellfoundry.models.install_config import (
    DEFAULT_AUTHOR,
    DEFAULT_DOMAIN,
    DEFAULT_GITHUB_LOGIN,
    DEFAULT_GITHUB_PASSWORD,
    DEFAULT_HOST,
    DEFAULT_ONLINE_MODE,
    DEFAULT_PASSWORD,
    DEFAULT_PORT,
    DEFAULT_TEMPLATE_LOCATION,
    DEFAULT_USERNAME,
    InstallConfig,
)
from shellfoundry.models.shellfoundry_settings import (
    DEFAULT_DEFAULT_VIEW,
    ShellFoundrySettings,
)
from shellfoundry.utilities.config.config_providers import DefaultConfigProvider

INSTALL = "install"

HOST = "host"
PORT = "port"
USERNAME = "username"
PASSWORD = "password"
DOMAIN = "domain"
AUTHOR = "author"
ONLINE_MODE = "online_mode"
TEMPLATE_LOCATION = "template_location"
GITHUB_LOGIN = "github_login"
GITHUB_PASSWORD = "github_password"

DEFAULT_VIEW = "defaultview"

if TYPE_CHECKING:
    from shellfoundry.utilities.config.config_providers import ConfigProvider


@define
class Configuration:
    reader: CloudShellConfigReader
    config_provider: ConfigProvider | None = field(factory=DefaultConfigProvider)

    def read(self) -> InstallConfig:
        config_path = self.config_provider.get_config_path()

        if config_path is None or not os.path.isfile(config_path):
            return self.reader.get_defaults()

        with open(config_path) as stream:
            config = yaml.safe_load(stream.read())

        if not config or INSTALL not in config:
            return self.reader.get_defaults()

        return self.reader.read_from_config(config[INSTALL])

    @staticmethod
    def readall(config_path: str, mark_defaults: str | None = None) -> dict[str, dict]:
        """Reads configuration from given file.

        Missing keys will be filled with their defaults.
        """
        config_data = None
        if os.path.exists(config_path):
            with open(config_path, encoding="utf8") as conf_file:
                config_data = yaml.safe_load(conf_file)

        if not config_data or INSTALL not in config_data:
            config_data = {INSTALL: {}}

        mark_defaults_f = Configuration._mark_defaults
        install_cfg_def = {
            (k, mark_defaults_f(v, mark_defaults))
            for k, v in asdict(InstallConfig.get_default()).items()
        }
        sf_cfg_def = {
            (k, mark_defaults_f(v, mark_defaults))
            for k, v in asdict(ShellFoundrySettings.get_default()).items()
        }
        all_cfg = dict(install_cfg_def)
        all_cfg.update(sf_cfg_def)
        all_cfg.update(config_data[INSTALL])
        return {INSTALL: all_cfg}

    @staticmethod
    def _mark_defaults(value: str | int, mark_defaults_char: str | None) -> str:
        return f"{value} {mark_defaults_char}" if mark_defaults_char else str(value)


class CloudShellConfigReader:
    @staticmethod
    def get_defaults():
        return InstallConfig.get_default()

    @staticmethod
    def read_from_config(config: dict[str, str]) -> InstallConfig:
        if not config:
            return CloudShellConfigReader.get_defaults()

        return InstallConfig(
            config.get(HOST, DEFAULT_HOST),
            config.get(PORT, DEFAULT_PORT),
            config.get(USERNAME, DEFAULT_USERNAME),
            config.get(PASSWORD, DEFAULT_PASSWORD),
            config.get(DOMAIN, DEFAULT_DOMAIN),
            config.get(AUTHOR, DEFAULT_AUTHOR),
            config.get(ONLINE_MODE, DEFAULT_ONLINE_MODE),
            config.get(TEMPLATE_LOCATION, DEFAULT_TEMPLATE_LOCATION),
            config.get(GITHUB_LOGIN, DEFAULT_GITHUB_LOGIN),
            config.get(GITHUB_PASSWORD, DEFAULT_GITHUB_PASSWORD),
        )


class ShellFoundryConfig:
    @staticmethod
    def get_defaults():
        return ShellFoundrySettings.get_default()

    @staticmethod
    def read_from_config(config: dict[str, str]) -> ShellFoundrySettings:
        if not config:
            return ShellFoundryConfig.get_defaults()
        return ShellFoundrySettings(config.get(DEFAULT_VIEW, DEFAULT_DEFAULT_VIEW))
