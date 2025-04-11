from __future__ import annotations

from functools import update_wrapper

import click
from attrs import define, field

from shellfoundry.exceptions import ShellFoundryVersionException
from shellfoundry.utilities import is_index_version_greater_than_current
from shellfoundry.utilities.config_reader import CloudShellConfigReader, Configuration


@define
class shellfoundry_version_check:
    abort_if_major: bool = False
    cloudshell_config_reader: Configuration = field(
        factory=lambda: Configuration(CloudShellConfigReader())
    )

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
