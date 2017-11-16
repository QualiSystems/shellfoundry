import os
import click

GLOBAL_CONFIG_NAME = 'global_config.yml'
LOCAL_CONFIG_NAME = 'cloudshell_config.yml'


class LocalConfigProvider(object):
    def get_config_path(self):
        path = os.path.join(os.getcwd(), LOCAL_CONFIG_NAME)
        if os.path.exists(path):
            click.echo('Using local configuration...')
        return path


class GlobalConfigProvider(object):
    QUALI = 'Quali'
    PRODUCT = 'shellfoundry'

    def get_config_path(self):
        sf_name = os.path.join(GlobalConfigProvider.QUALI, GlobalConfigProvider.PRODUCT)
        app_dir_path = click.get_app_dir(sf_name)
        return os.path.join(app_dir_path, GLOBAL_CONFIG_NAME)


class ConfigProvider(object):
    def __init__(self, *args):
        self.config_providers = args

    def get_config_path(self):
        for provider in self.config_providers:
            config_path = provider.get_config_path()
            if os.path.exists(config_path):
                return config_path


class DefaultConfigProvider(ConfigProvider):
    def __init__(self):
        ConfigProvider.__init__(self, (GlobalConfigProvider()))  # The order do matters
        self.default_provider = LocalConfigProvider()
        # self.fallback_provider = LocalConfigProvider()

    def get_config_path(self):
        config_path = self.default_provider.get_config_path()
        if not os.path.exists(config_path):
            config_path = ConfigProvider.get_config_path(self)
        return config_path  # or self.fallback_provider.get_config_path()
