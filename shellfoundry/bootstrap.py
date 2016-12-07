import os

import click
import pkg_resources
from cloudshell.rest.api import PackagingRestApiClient
from cloudshell.rest.exceptions import ShellNotFoundException
from requests import post

from shellfoundry.commands.dist_command import DistCommandExecutor
from shellfoundry.commands.generate_command import GenerateCommandExecutor
from shellfoundry.commands.install_command import InstallCommandExecutor
from shellfoundry.commands.list_command import ListCommandExecutor
from shellfoundry.commands.new_command import NewCommandExecutor
from shellfoundry.commands.pack_command import PackCommandExecutor
from shellfoundry.commands.config_command import ConfigCommandExecutor
from shellfoundry.utilities.shell_package import ShellPackage


@click.group()
def cli():
    pass


@cli.command()
def version():
    """
    Displays the shellfoundry version
    """
    click.echo(u'shellfoundry version ' + pkg_resources.get_distribution(u'shellfoundry').version)


@cli.command()
@click.option(u'--tosca', 'template_type', flag_value='tosca')
@click.option(u'--legacy', 'template_type', flag_value='legacy')
@click.option(u'--all', 'template_type', flag_value='all', default=True)
def list(template_type):
    """
    Lists the available shell templates
    """
    ListCommandExecutor(template_type).list()


@cli.command()
@click.argument(u'name')
@click.option(u'--template', default=u'resource',
              help="Specify a Shell template. Use 'shellfoundry list' to see the list of available templates. "
                   "You can use 'local://<foler>' to specify a locally saved template")
def new(name, template):
    """
    Creates a new shell based on a template
    """
    NewCommandExecutor().new(name, template)


@cli.command()
def pack():
    """
    Creates a shell package
    """
    PackCommandExecutor().pack()


@cli.command()
def install():
    """
    Installs the shell package into CloudShell
    """
    PackCommandExecutor().pack()
    InstallCommandExecutor().install()


@cli.command()
def dist():
    """
    Creates a deployable Shell which can be distributed to a production environment
    """
    PackCommandExecutor().pack()
    DistCommandExecutor().dist()


@cli.command()
def generate():
    """
    Generates Python driver data model to be used in driver code
    """
    PackCommandExecutor().pack()
    GenerateCommandExecutor().generate()

@cli.command()
@click.argument(u'kv', type=(str, str), default=(None, None), required=False)
@click.option('--global/--local', 'global_cfg', default=True)
@click.option('--remove', 'key_to_remove', default=None)
def config(kv, global_cfg, key_to_remove):
    """
    Configures global/local config values to allow deployment over cloudshell
    """
    ConfigCommandExecutor(global_cfg).config(kv, key_to_remove)
