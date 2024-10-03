#!/usr/bin/python
# -*- coding: utf-8 -*-

import click


class ConfigRecord(object):
    def __init__(self, key, value=None):
        self.key = key
        self.value = value

    def save(self, config_context):
        if config_context.try_save(self.key, self.value):
            click.echo("{}: {} was saved successfully".format(self.key, self.value))
        else:
            click.echo("Failed to save key value")

    def delete(self, config_context):
        if config_context.try_delete(self.key):
            click.echo("{} was deleted successfully".format(self.key))
        else:
            # add support for typed exceptions
            # in order to have the ability to differentiate between failures
            click.echo("Failed to delete key")
