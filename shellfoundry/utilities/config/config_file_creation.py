from __future__ import annotations

import errno
import os

import click


class ConfigFileCreation:
    @staticmethod
    def create(config_file_path: str) -> None:
        if os.path.exists(config_file_path):
            return
        if not os.path.exists(os.path.dirname(config_file_path)):
            try:
                dirname = os.path.dirname(config_file_path)
                os.makedirs(dirname)
            except OSError as exc:
                if exc.errno != errno.EEXIST:
                    click.echo("Failed to create config file")
                    click.echo(str(exc))
                    raise
        try:
            click.echo("Creating config file...")
            with open(config_file_path, mode="w", encoding="utf8"):
                pass
        except Exception:
            if not os.path.exists(config_file_path):
                click.echo("Failed to create config file")
                import sys

                click.echo(str(sys.exc_info()[1]))
                raise
