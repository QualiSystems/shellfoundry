import os
import click
import pkg_resources
from cookiecutter.main import cookiecutter
from qpm.packaging.shell_installer import ShellInstaller
from shellfoundry.package_builder import PackageBuilder


@click.group()
def cli():
    click.echo('shellfoundry, version ' + pkg_resources.get_distribution("qpm").version)
    pass


@cli.command()
def version():
    """
    Prints the current version of shellfoundry
    :return:
    """
    pass


@cli.command()
def list():
    """
    Lists CloudShell shell templates
    :return:
    """
    click.echo('Should print templates list')


@cli.command()
@click.argument(u'template')
def new(template):
    """
    Create a new CloudShell shell based on a template
    :param template: CloudShell shell template to be used.
    :return:
    """
    cookiecutter(template)


@cli.command()
@click.argument(u'package')
@click.option(u'--path', default=None)
def build(package, path):
    """
    Builds a CloudShell package
    :param package: Package name
    :param path: Path to the source directory
    :return:
    """
    click.echo('package is ' + package)
    click.echo('path is ' + (path or ''))
    current_path = path or os.getcwd()
    package_builder = PackageBuilder()
    package_builder.build_package(current_path, package)


@cli.command()
@click.argument(u'package')
def install(package):
    """
    Installs a CloudShell package into CloudShell
    :param package:
    :return:
    """
    installer = ShellInstaller()
    installer.install(package)


if __name__ == '__main__':
    cli()


