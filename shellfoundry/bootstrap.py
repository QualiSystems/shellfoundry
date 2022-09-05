#!/usr/bin/python
# -*- coding: utf-8 -*-

import click
import pkg_resources

from shellfoundry.commands.config_command import ConfigCommandExecutor
from shellfoundry.commands.delete_command import DeleteCommandExecutor
from shellfoundry.commands.dist_command import DistCommandExecutor
from shellfoundry.commands.extend_command import ExtendCommandExecutor
from shellfoundry.commands.generate_command import GenerateCommandExecutor
from shellfoundry.commands.get_templates_command import GetTemplatesCommandExecutor
from shellfoundry.commands.install_command import InstallCommandExecutor
from shellfoundry.commands.list_command import ListCommandExecutor
from shellfoundry.commands.new_command import NewCommandExecutor
from shellfoundry.commands.pack_command import PackCommandExecutor
from shellfoundry.commands.show_command import ShowCommandExecutor
from shellfoundry.decorators import shellfoundry_version_check
from shellfoundry.utilities import GEN_ONE, GEN_TWO, LAYER_ONE, NO_FILTER


@click.group()
def cli():
    pass


@cli.command()
def version():
    """Displays the shellfoundry version."""
    click.echo(
        "shellfoundry version " + pkg_resources.get_distribution("shellfoundry").version
    )


@cli.command()  # noqa: A001
@click.option(
    "--gen2",
    "default_view",
    flag_value=GEN_TWO,
    help="Show 2nd generation shell templates",
)
@click.option(
    "--gen1",
    "default_view",
    flag_value=GEN_ONE,
    help="Show 1st generation shell templates",
)
@click.option(
    "--layer1", "default_view", flag_value=LAYER_ONE, help="Show layer1 shell templates"
)
@click.option("--all", "default_view", flag_value=NO_FILTER, help="Show all templates")
@shellfoundry_version_check(abort_if_major=True)
def list(default_view):  # noqa: A001
    """Lists the available shell templates."""
    ListCommandExecutor(default_view).list()


@cli.command()
@click.argument("name")
@click.option(
    "--template",
    default="gen2/resource",
    help="Specify a Shell template. Use 'shellfoundry list' to see the list of available templates. "  # noqa: E501
    "You can use 'local://<folder>' to specify a locally saved template",
)
@click.option("--version", default=None)
@click.option(
    "--python",
    type=click.Choice(["2", "3"]),
    default="3",
    required=False,
    help="Specify Python version which will be used",
)
@shellfoundry_version_check(abort_if_major=True)
def new(name, template, version, python):
    """Creates a new shell based on a template."""
    NewCommandExecutor().new(name, template, version, python)


@cli.command()
def pack():
    """Creates a shell package."""
    PackCommandExecutor().pack()


@cli.command()
def install():
    """Installs the shell package into CloudShell."""
    PackCommandExecutor().pack()
    InstallCommandExecutor().install()


@cli.command()
@click.option(
    "--enable_cs_repo",
    is_flag=True,
    help="Includes shell dependencies " "that are stored in the local pypi repository",
)
def dist(enable_cs_repo):
    """Creates a deployable Shell which can be distributed to a production environment."""  # noqa: E501
    PackCommandExecutor().pack()
    DistCommandExecutor().dist(enable_cs_repo)


@cli.command()
def generate():
    """Generates Python driver data model to be used in driver code."""
    PackCommandExecutor().pack()
    GenerateCommandExecutor().generate()


@cli.command()
@click.argument("kv", type=(str, str), default=(None, None), required=False)
@click.option("--global/--local", "global_cfg", default=True)
@click.option("--remove", "key_to_remove", default=None)
def config(kv, global_cfg, key_to_remove):
    """Configures global/local config values used by shellfoundry."""
    ConfigCommandExecutor(global_cfg).config(kv, key_to_remove)


@cli.command()
@click.argument("template_name")
def show(template_name):
    """Shows all versions of TEMPLATE NAME."""
    ShowCommandExecutor().show(template_name)


@cli.command()
@click.argument("source")
@click.option(
    "--attribute",
    "add_attribute",
    multiple=True,
    default=None,
    help="Creates a commented out attribute in the shell definition",
)
def extend(source, add_attribute):
    r"""Creates a new shell based on an existing shell.

    SOURCE - Specify the original Shell location.\n
    \tYou can use 'local://<folder>' to specify a locally saved Shell folder
    """
    ExtendCommandExecutor().extend(source, add_attribute)


@cli.command()
@click.argument("cs_version")
@click.option(
    "--output_dir",
    "output_dir",
    default=None,
    help="Folder where templates will be saved",
)
def get_templates(cs_version, output_dir):
    """Download all templates which are compatible with provided CloudShell Version.

    CS_VERSION - CloudShell Version
    """
    GetTemplatesCommandExecutor().get_templates(cs_version, output_dir)


@cli.command()
@click.argument("name")
def delete(name):
    """Deletes the shell from CloudShell.

    NAME - Shell name installed on CloudShell
    """
    DeleteCommandExecutor().delete(name)
