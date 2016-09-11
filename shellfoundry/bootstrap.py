import os

import click
import pkg_resources
from cloudshell.rest.api import PackagingRestApiClient
from cloudshell.rest.exceptions import ShellNotFoundException
from requests import post

from shellfoundry.commands.dist_command import DistCommandExecutor
from shellfoundry.commands.install_command import InstallCommandExecutor
from shellfoundry.commands.list_command import ListCommandExecutor
from shellfoundry.commands.new_command import NewCommandExecutor
from shellfoundry.commands.pack_command import PackCommandExecutor
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
    Creates a deployable Shell which can be distributed to a production environment
    """
    PackCommandExecutor().pack()
    DistCommandExecutor().dist()


@cli.command()
def generate():
    """
    Creates a deployable Shell which can be distributed to a production environment
    """
    path = os.getcwd()
    shell_package = ShellPackage(path)
    shell_filename = shell_package.get_shell_name() + '.zip'
    package_full_path = os.path.join(path, 'dist', shell_filename)

    client = PackagingRestApiClient(ip='localhost',
                                    username='admin',
                                    port='9000',
                                    domain='global',
                                    password='admin')

    url = 'http://localhost:9000/API/ShellDrivers/Generate'
    response = post(url,
                    files={os.path.basename(shell_filename): open(package_full_path, 'rb')},
                    headers={'Authorization': 'Basic ' + client.token})

    print('writing zip file')
    with open('my_driver.zip', 'wb') as driver_file:
        driver_file.write(response.content)

generate()
