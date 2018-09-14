#!/usr/bin/python
# -*- coding: utf-8 -*-

import click

from shellfoundry.utilities.config_reader import Configuration, INSTALL
from shellfoundry.utilities.config.config_context import ConfigContext
from shellfoundry.utilities.config.config_providers import LocalConfigProvider, GlobalConfigProvider
from shellfoundry.utilities.config.config_record import ConfigRecord
from shellfoundry.utilities.config.config_file_creation import ConfigFileCreation
from textwrap import wrap

DEFAULTS_CHAR = "*"


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
            field, name = kv
            if not name:
                raise click.BadArgumentUsage("Field '{}' cannot be empty".format(field))
            else:
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

        config_data = Configuration.readall(config_file_path, mark_defaults=DEFAULTS_CHAR)
        table = self._format_config_as_table(config_data, DEFAULTS_CHAR)
        click.echo(table)
        click.echo('')
        click.echo(
            "* Values marked with '{}' are the default values and were not changed by the user.".format(
                DEFAULTS_CHAR))

    def _format_config_as_table(self, config_data, defaults_char):
        from shellfoundry.utilities.modifiers.configuration.password_modification import PasswordModification
        table_data = [['Key', 'Value', 'D', 'Description']]
        for key, value in config_data[INSTALL].iteritems():
            default_val = ''
            if defaults_char in value:
                default_val = defaults_char
                value = value.strip(defaults_char).lstrip()
            if key == PasswordModification.HANDLING_KEY:
                value = '[encrypted]'
            table_data.append([key, "\n".join(wrap(value, 23)), default_val, ""])
        import terminaltables
        table = terminaltables.SingleTable(table_data)
        table.outer_border = False
        table.inner_column_border = False
        table.inner_row_border = False

        max_width = table.column_max_width(3)
        for row in range(1, len(table.table_data)):
            table.table_data[row][3] = "\n".join(wrap(Configuration.get_key_description(table.table_data[row][0]), max_width))

        return table.table

    @staticmethod
    def _get_config_file_path(is_global_flag):
        if is_global_flag:
            cfg_provider = GlobalConfigProvider()
            return cfg_provider.get_config_path()
        return LocalConfigProvider().get_config_path()
