from __future__ import annotations

import os
from typing import ClassVar

import click

GLOBAL_CONFIG_NAME = "global_config.yml"
LOCAL_CONFIG_NAME = "cloudshell_config.yml"


class LocalConfigProvider:
    def get_config_path(self):
        path = os.path.join(os.getcwd(), LOCAL_CONFIG_NAME)
        if os.path.exists(path):
            click.echo("Using local configuration...")
        return path


class GlobalConfigProvider:
    QUALI: ClassVar[str] = "Quali"
    PRODUCT: ClassVar[str] = "shellfoundry"

    def get_config_path(self):
        sf_name = os.path.join(GlobalConfigProvider.QUALI, GlobalConfigProvider.PRODUCT)
        app_dir_path = click.get_app_dir(sf_name)
        return os.path.join(app_dir_path, GLOBAL_CONFIG_NAME)


class ConfigProvider:
    def __init__(self, *args):
        self.config_providers = args

    def get_config_path(self) -> str | None:
        for provider in self.config_providers:
            config_path = provider.get_config_path()
            if os.path.exists(config_path):
                return config_path


class DefaultConfigProvider(ConfigProvider):
    def __init__(self):
        ConfigProvider.__init__(self, (GlobalConfigProvider()))  # The order do matters
        self.default_provider = LocalConfigProvider()

    def get_config_path(self) -> str:
        config_path = self.default_provider.get_config_path()
        if not os.path.exists(config_path):
            config_path = ConfigProvider.get_config_path(self)
        return config_path  # or self.fallback_provider.get_config_path()
