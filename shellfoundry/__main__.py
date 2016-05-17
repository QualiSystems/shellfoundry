import os
import click
import pkg_resources
from cookiecutter.main import cookiecutter
from shellfoundry.config_reader import ConfigReader
from shellfoundry.installer import ShellInstaller
from shellfoundry.package_builder import PackageBuilder
from shellfoundry.template_retriever import TemplateRetriever


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
    template_retriever = TemplateRetriever()
    templates = template_retriever.get_templates()
    click.echo('Supported templates are: \r\n {0}'.format(_get_templates_with_comma(templates)))


@cli.command()
@click.argument(u'template')
def new(template):
    """
    Create a new CloudShell shell based on a template
    :param template: CloudShell shell template to be used.
    :return:
    """
    template_retriever = TemplateRetriever()
    templates = template_retriever.get_templates()

    if template not in templates:
        raise click.BadParameter(
            'Template {0} does not exist. Supported templates are: {1}'.format(template,
                                                                               _get_templates_with_comma(templates)))

    cookiecutter(templates[template])


def _get_templates_with_comma(templates):
    return ', '.join(templates.keys())


@cli.command()
@click.option(u'--path', default=None)
def build(path):
    """
    Builds a CloudShell package
    :param path: Path to the source directory
    :return:
    """
    config_reader = ConfigReader()
    package_builder = PackageBuilder()

    project = config_reader.read()
    current_path = path or os.getcwd()
    package_builder.build_package(current_path, project.name)


@cli.command()
def install():
    """
    Installs a CloudShell shell into CloudShell
    :return:
    """
    config_reader = ConfigReader()
    installer = ShellInstaller()
    project = config_reader.read()
    installer.install(project.name, project.install)


if __name__ == '__main__':
    cli()
