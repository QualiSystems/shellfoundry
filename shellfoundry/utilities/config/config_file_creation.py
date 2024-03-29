#!/usr/bin/python
# -*- coding: utf-8 -*-
import errno
import os
from io import open

import click


class ConfigFileCreation(object):
    def create(self, config_file_path):
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
            open(config_file_path, mode="w", encoding="utf8").close()
        except Exception:
            if not os.path.exists(config_file_path):
                click.echo("Failed to create config file")
                import sys

                click.echo(str(sys.exc_info()[1]))
                raise
