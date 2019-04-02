#!/usr/bin/python
# -*- coding: utf-8 -*-

import click

from functools import update_wrapper

from shellfoundry.exceptions import ShellFoundryVersionException
from shellfoundry.utilities import is_index_version_greater_than_current
from shellfoundry.utilities.config_reader import Configuration, CloudShellConfigReader


class shellfoundry_version_check(object):
    def __init__(self, abort_if_major=False):
        self.abort_if_major = abort_if_major
        self.cloudshell_config_reader = Configuration(CloudShellConfigReader())

    def __call__(self, f):
        def decorator(*args, **kwargs):
            output = ''
            if self.cloudshell_config_reader.read().online_mode.lower() == "true":
                try:
                    is_greater_version, is_major_release = is_index_version_greater_than_current()
                except ShellFoundryVersionException, err:
                    click.secho(err.message, fg='red')
                    raise click.Abort()
                if is_greater_version:
                    if is_major_release:
                        output = 'This version of shellfoundry is not supported anymore, ' \
                                 'please upgrade by running: pip install shellfoundry --upgrade'

                        if self.abort_if_major:
                            click.secho(output, fg='yellow')
                            print ''
                            raise click.Abort()
                    else:
                        output = 'There is a new version of shellfoundry available, ' \
                                 'please upgrade by running: pip install shellfoundry --upgrade'

            f(**kwargs)

            if output:
                print ''
                click.secho(output, fg='yellow')

        return update_wrapper(decorator, f)
