# !/usr/bin/python
# -*- coding: utf-8 -*-

import click
from shellfoundry.utilities.shell_package_installer import ShellPackageInstaller
from shellfoundry.exceptions import FatalError


class DeleteCommandExecutor(object):
    def __init__(self, shell_package_installer=None):
        self.shell_package_installer = shell_package_installer or ShellPackageInstaller()

    def delete(self, shell_name):
        try:
            self.shell_package_installer.delete(shell_name=shell_name)
        except FatalError as err:

            msg = err.message if hasattr(err, "message") else err.args[0]
            # print(type(err.args), err.args)
            click.ClickException(msg)

        click.secho('Successfully deleted shell', fg='green')
