from __future__ import annotations

import click
from attrs import define, field

from shellfoundry.utilities.config.config_context import ConfigContext
from shellfoundry.utilities.config.config_file_creation import ConfigFileCreation
from shellfoundry.utilities.config.config_providers import (
    GlobalConfigProvider,
    LocalConfigProvider,
)
from shellfoundry.utilities.config.config_record import ConfigRecord
from shellfoundry.utilities.config_reader import INSTALL, Configuration

DEFAULTS_CHAR = "*"


@define
class ConfigCommandExecutor:
    global_cfg: bool
    cfg_creation: ConfigFileCreation = field(factory=ConfigFileCreation)

    def config(
        self,
        kv: tuple[str | None, str | None] = (None, None),
        key_to_remove: str = None,
    ) -> None:
        config_file_path = self._get_config_file_path(self.global_cfg)
        if key_to_remove is not None:  # remove key
            context = ConfigContext(config_file_path)
            ConfigRecord(key_to_remove).delete(context)
        elif None not in kv:  # append key
            config_key, config_value = kv
            if not config_value:
                raise click.BadArgumentUsage(f"Field '{config_key}' can not be empty")
            else:
                self.cfg_creation.create(config_file_path)
                context = ConfigContext(config_file_path)
                ConfigRecord(*kv).save(context)
        else:
            self._echo_config(config_file_path)

    def _echo_config(self, config_file_path: str) -> None:
        """Print current configuration."""
        config_data = Configuration.readall(
            config_file_path, mark_defaults=DEFAULTS_CHAR
        )
        table = self._format_config_as_table(config_data, DEFAULTS_CHAR)
        click.echo(table)
        click.echo("")
        click.echo(
            f"* Value marked with '{DEFAULTS_CHAR}' "
            f"is actually the default value and has not been override by the user."
        )

    @staticmethod
    def _format_config_as_table(
        config_data: dict[str, dict], defaults_char: str
    ) -> str:
        """Format configuration in readable table view."""
        import terminaltables

        from shellfoundry.utilities.modifiers.configuration.password_modification import (  # noqa: E501
            PasswordModification,
        )

        table_data = [["Key", "Value", ""]]
        for key, value in config_data[INSTALL].items():
            default_val = ""
            if defaults_char in value:
                default_val = defaults_char
                value = value.strip(defaults_char).lstrip()
            if key in PasswordModification.HANDLING_KEYS:
                value = "[encrypted]"
            table_data.append([key, value, default_val])

        table = terminaltables.AsciiTable(table_data)
        table.outer_border = False
        table.inner_column_border = False
        return table.table

    @staticmethod
    def _get_config_file_path(is_global_flag: bool) -> str:
        if is_global_flag:
            cfg_provider = GlobalConfigProvider()
            return cfg_provider.get_config_path()
        return LocalConfigProvider().get_config_path()
