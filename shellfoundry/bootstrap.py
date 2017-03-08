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
from shellfoundry.commands.show_command import ShowCommandExecutor
from shellfoundry.utilities.shell_package import ShellPackage
from shellfoundry.utilities import GEN_ONE, GEN_TWO, LAYER_ONE, NO_FILTER


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
@click.option(u'--gen2', 'default_view', flag_value=GEN_TWO, help="Show 2nd generation shell templates")
@click.option(u'--gen1', 'default_view', flag_value=GEN_ONE, help="Show 1st generation shell templates")
@click.option(u'--layer1', 'default_view', flag_value=LAYER_ONE, help="Show layer1 shell templates")
@click.option(u'--all', 'default_view', flag_value=NO_FILTER, help="Show all templates")
def list(default_view):
    """
    Lists the available shell templates
    """
    ListCommandExecutor(default_view).list()


@cli.command()
@click.argument(u'name')
@click.option(u'--template', default=u'gen2/resource',
              help="Specify a Shell template. Use 'shellfoundry list' to see the list of available templates. "
                   "You can use 'local://<foler>' to specify a locally saved template")
@click.option(u'--version', default=None)
def new(name, template, version):
    """
    Creates a new shell based on a template
    """
    NewCommandExecutor().new(name, template, version)


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

@cli.command()
@click.argument(u'template_name')
def show(template_name):
    """
    Shows all versions of TEMPLATENAME
    """
    ShowCommandExecutor().show(template_name)
