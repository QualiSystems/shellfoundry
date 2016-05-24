import click
import pkg_resources

from shellfoundry.commands.install_command import InstallCommandExecutor
from shellfoundry.commands.list_command import ListCommandExecutor
from shellfoundry.commands.new_command import NewCommandExecutor
from shellfoundry.commands.pack_command import PackCommandExecutor


@click.group()
def cli():
    click.echo(u'shellfoundry - CloudShell shell command-line tool')
    pass


@cli.command()
def version():
    """
    Show shellfoundry version.
    """
    click.echo(u'Version: ' + pkg_resources.get_distribution(u'shellfoundry').version)


@cli.command()
def list():
    """
    List shell templates.
    """
    ListCommandExecutor().list()


@cli.command()
@click.argument(u'name')
@click.option(u'--template', default=u'base', help='Template to be used')
def new(name, template):
    """
    Create a new shell based on a template.\r\n
    """
    NewCommandExecutor().new(name, template)


@cli.command()
def pack():
    """
    Pack the shell package.
    """
    PackCommandExecutor().pack()


@cli.command()
def install():
    """
    Install the shell package into CloudShell.
    """
    InstallCommandExecutor().install()
