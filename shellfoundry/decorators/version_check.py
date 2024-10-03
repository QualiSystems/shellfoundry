#!/usr/bin/python
# -*- coding: utf-8 -*-
from functools import update_wrapper

import click

from shellfoundry.exceptions import ShellFoundryVersionException
from shellfoundry.utilities import is_index_version_greater_than_current
from shellfoundry.utilities.config_reader import CloudShellConfigReader, Configuration


class shellfoundry_version_check(object):
    def __init__(self, abort_if_major=False):
        self.abort_if_major = abort_if_major
        self.cloudshell_config_reader = Configuration(CloudShellConfigReader())

    def __call__(self, f):
        def decorator(*args, **kwargs):
            output = ""
            if self.cloudshell_config_reader.read().online_mode.lower() == "true":
                try:
                    (
                        is_greater_version,
                        is_major_release,
                    ) = is_index_version_greater_than_current()
                except ShellFoundryVersionException as err:
                    click.secho(str(err), fg="red")
                    raise click.Abort()
                if is_greater_version:
                    if is_major_release:
                        output = (
                            "This version of shellfoundry is not supported anymore, "
                            "please upgrade by running: pip install shellfoundry --upgrade"  # noqa: E501
                        )

                        if self.abort_if_major:
                            click.secho(output, fg="yellow")
                            print("")  # noqa: T001
                            raise click.Abort()
                    else:
                        output = (
                            "There is a new version of shellfoundry available, "
                            "please upgrade by running: pip install shellfoundry --upgrade"  # noqa: E501
                        )

            f(**kwargs)

            if output:
                print("")  # noqa: T001
                click.secho(output, fg="yellow")

        return update_wrapper(decorator, f)
