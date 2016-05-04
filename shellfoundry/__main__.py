from qpm.packaging.auto_argument_parser import AutoArgumentParser
from shellfoundry.gateway import ShellFoundryGateway
import click


@click.group()
def cli():
    click.echo('cli')
    pass


@click.command()
@click.argument(u'template')
def create(template):
    click.echo('create' + template)
    # argument_parser = AutoArgumentParser(ShellFoundryGateway)
    # argument_parser.parse_args()


@click.command()
@click.argument(u'package')
def pack(package):
    click.echo('pack' + package)


@click.command()
@click.argument(u'package')
def install(package):
    click.echo('install' + package)

cli.add_command(create)
cli.add_command(pack)
cli.add_command(install)

if __name__ == '__main__':
    cli()


