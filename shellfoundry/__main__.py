import os
import click
import pkg_resources
from cookiecutter.main import cookiecutter
from shellfoundry.installer import ShellInstaller
from shellfoundry.package_builder import PackageBuilder
from shellfoundry.template_retriever import TemplateRetriever
from shellfoundry.config_reader import ConfigReader


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
    template_retriever = TemplateRetriever()
    templates = template_retriever.get_templates()
    click.echo(u'Supported templates are: \r\n {0}'.format(_get_templates_with_comma(templates)))


@cli.command()
@click.option(u'--name', prompt=u'Type shell name:', help=u'Shell name to be created.')
@click.option(u'--template', default=u'default', help=u'Shell template to be used.')
def new(name, template):
    """
    Create a new shell based on a template.
    """
    template_retriever = TemplateRetriever()
    templates = template_retriever.get_templates()

    if template not in templates:
        raise click.BadParameter(
            u'Template {0} does not exist. Supported templates are: {1}'.format(template,
                                                                                _get_templates_with_comma(templates)))

    cookiecutter(templates[template], no_input=True, extra_context={u'project_name': name})


def _get_templates_with_comma(templates):
    return ', '.join(templates.keys())


@cli.command()
def pack():
    """
    Pack the shell package.
    """
    config_reader = ConfigReader()
    package_builder = PackageBuilder()

    project = config_reader.read()
    current_path = os.getcwd()
    package_builder.build_package(current_path, project.name)


@cli.command()
def install():
    """
    Install the shell package into CloudShell.
    """
    config_reader = ConfigReader()
    installer = ShellInstaller()
    project = config_reader.read()
    installer.install(project.name, project.install)


if __name__ == '__main__':
    cli()
