# !/usr/bin/python
# -*- coding: utf-8 -*-

import click
from shellfoundry.utilities.shell_package_installer import ShellPackageInstaller


class DeleteCommandExecutor(object):
    def __init__(self, shell_package_installer=None):
        self.shell_package_installer = shell_package_installer or ShellPackageInstaller()

    def delete(self, shell_name):
        self.shell_package_installer.delete(shell_name=shell_name)
        click.secho('Successfully deleted shell', fg='green')
