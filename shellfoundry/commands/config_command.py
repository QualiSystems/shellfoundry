import click
import yaml

from shellfoundry.utilities.config_reader import INSTALL
from shellfoundry.utilities.config.config_context import ConfigContext
from shellfoundry.utilities.config.config_providers import LocalConfigProvider, GlobalConfigProvider
from shellfoundry.utilities.config.config_record import ConfigRecord
from shellfoundry.utilities.config.config_file_creation import ConfigFileCreation


class ConfigCommandExecutor(object):
    def __init__(self, global_cfg, cfg_creation=None):
        self.global_cfg = global_cfg
        self.cfg_creation = cfg_creation or ConfigFileCreation()

    def config(self, kv=(None, None), key_to_remove=None):
        config_file_path = self._get_config_file_path(self.global_cfg)
        if self._should_remove_key(key_to_remove):
            context = ConfigContext(config_file_path)
            ConfigRecord(key_to_remove).delete(context)
        elif self._should_append_key(kv):
            self.cfg_creation.create(config_file_path)
            context = ConfigContext(config_file_path)
            ConfigRecord(*kv).save(context)
        else:
            self._echo_config(config_file_path)

    def _should_append_key(self, kv):
        return None not in kv

    def _should_remove_key(self, key_to_remove):
        return key_to_remove is not None

    def _echo_config(self, config_file_path):
        config_data = self._extract_config_data(config_file_path)
        if not config_data:
            click.echo("{} config does not exists".format(self._interpret_config_type()))
            return
        if INSTALL not in config_data:
            click.echo('{} config file has no \'install\' section.'.format(self._interpret_config_type()))
            return
        for key, value in config_data[INSTALL].iteritems():
            if key == 'password':
                value = '[encrypted]'
            s = '{}: {}'.format(key, value)
            click.echo(s)

    @staticmethod
    def _get_config_file_path(is_global_flag):
        if is_global_flag:
            cfg_provider = GlobalConfigProvider()
            return cfg_provider.get_config_path()
        return LocalConfigProvider().get_config_path()

    @staticmethod
    def _extract_config_data(config_file_path):
        import os
        if not os.path.exists(config_file_path):
            return None
        with open(config_file_path, mode='r') as conf_file:
            return yaml.load(conf_file)

    def _interpret_config_type(self):
        return 'Global' if self.global_cfg else 'Local'


