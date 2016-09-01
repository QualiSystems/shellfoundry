import click
import pkg_resources

from shellfoundry.commands.dist_command import DistCommandExecutor
from shellfoundry.commands.install_command import InstallCommandExecutor
from shellfoundry.commands.list_command import ListCommandExecutor
from shellfoundry.commands.new_command import NewCommandExecutor
from shellfoundry.commands.pack_command import PackCommandExecutor


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
def list():
    """
    Lists the available shell templates
    """
    ListCommandExecutor().list()


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
    Downloads the driver's dependencies from PyPI to dist/offline_requirements
    """
    DistCommandExecutor().dist()
