#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
from io import open

import yaml

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


def get_with_default(install_config, parameter_name, default_value):
    """Get configuration with default values.

    :param install_config: A dict represents the install section inside the configuration file  # noqa: E501
    :param parameter_name: Specific key inside the install section
    :param default_value: Default value in cases that the key cannot be found
    :return: The value of the key in the configuration file or default value if key cannot be found  # noqa: E501
    """
    return (
        install_config[parameter_name]
        if install_config and parameter_name in install_config
        else default_value
    )


class Configuration(object):
    def __init__(self, reader, config_provider=None):
        self.reader = reader
        self.config_provider = config_provider or DefaultConfigProvider()

    def read(self):
        config_path = self.config_provider.get_config_path()

        if config_path is None or not os.path.isfile(config_path):
            return self.reader.get_defaults()

        with open(config_path) as stream:
            config = yaml.safe_load(stream.read())

        if not config or INSTALL not in config:
            return self.reader.get_defaults()

        return self.reader.read_from_config(config[INSTALL])

    @staticmethod
    def readall(config_path, mark_defaults=None):
        """Reads configuration from given file.

        Missing keys will be filled with their defaults.
        """
        config_data = None
        if os.path.exists(config_path):
            with open(config_path, mode="r", encoding="utf8") as conf_file:
                config_data = yaml.safe_load(conf_file)

        if not config_data or INSTALL not in config_data:
            config_data = {INSTALL: {}}

        mark_defaults_f = Configuration._mark_defaults
        install_cfg_def = {
            (k, mark_defaults_f(v, mark_defaults))
            for k, v in InstallConfig.get_default().__dict__.items()
        }
        sf_cfg_def = {
            (k, mark_defaults_f(v, mark_defaults))
            for k, v in ShellFoundrySettings.get_default().__dict__.items()
        }
        all_cfg = dict(install_cfg_def)
        all_cfg.update(sf_cfg_def)
        all_cfg.update(config_data[INSTALL])
        return {INSTALL: all_cfg}

    @staticmethod
    def _mark_defaults(value, mark_defaults_char):
        if not mark_defaults_char:
            return str(value)
        return "{value} {default_char}".format(
            value=str(value), default_char=mark_defaults_char
        )


class CloudShellConfigReader(object):
    def get_defaults(self):
        return InstallConfig.get_default()

    def read_from_config(self, config):
        host = get_with_default(config, HOST, DEFAULT_HOST)
        port = get_with_default(config, PORT, DEFAULT_PORT)
        username = get_with_default(config, USERNAME, DEFAULT_USERNAME)
        password = get_with_default(config, PASSWORD, DEFAULT_PASSWORD)
        domain = get_with_default(config, DOMAIN, DEFAULT_DOMAIN)
        author = get_with_default(config, AUTHOR, DEFAULT_AUTHOR)
        online_mode = get_with_default(config, ONLINE_MODE, DEFAULT_ONLINE_MODE)
        template_location = get_with_default(
            config, TEMPLATE_LOCATION, DEFAULT_TEMPLATE_LOCATION
        )
        github_login = get_with_default(config, GITHUB_LOGIN, DEFAULT_GITHUB_LOGIN)
        github_password = get_with_default(
            config, GITHUB_PASSWORD, DEFAULT_GITHUB_PASSWORD
        )
        return InstallConfig(
            host,
            port,
            username,
            password,
            domain,
            author,
            online_mode,
            template_location,
            github_login,
            github_password,
        )


class ShellFoundryConfig(object):
    def get_defaults(self):
        return ShellFoundrySettings.get_default()

    def read_from_config(self, config):
        defaultview = get_with_default(config, DEFAULT_VIEW, DEFAULT_DEFAULT_VIEW)
        return ShellFoundrySettings(defaultview)
