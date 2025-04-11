from __future__ import annotations

from typing import TYPE_CHECKING

import click
from attrs import define

if TYPE_CHECKING:
    from shellfoundry.utilities.config.config_context import ConfigContext


@define
class ConfigRecord:
    key: str
    value: str | None = None

    def save(self, config_context: ConfigContext) -> None:
        if config_context.try_save(self.key, self.value):
            click.echo(f"{self.key}: {self.value} was saved successfully")
        else:
            click.echo("Failed to save key value")

    def delete(self, config_context: ConfigContext) -> None:
        if config_context.try_delete(self.key):
            click.echo(f"{self.key} was deleted successfully")
        else:
            # add support for typed exceptions
            # in order to have the ability to differentiate between failures
            click.echo("Failed to delete key")
