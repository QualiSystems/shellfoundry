import click
import pkg_resources
from shellfoundry.config_reader import CloudShellConfigReader
from shellfoundry.installer import ShellInstaller
from shellfoundry.new_command import NewCommandExecutor
from shellfoundry.pack_command import PackCommandExecutor
from shellfoundry.template_retriever import TemplateRetriever


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
    click.echo(u'Supported templates are: \r\n {0}'.format(', '.join(templates.keys())))


@cli.command()
@click.argument(u'name')
@click.argument(u'template', default=u'default')
def new(name, template):
    """
    Create a new shell based on a template.
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
    config_reader = CloudShellConfigReader()
    installer = ShellInstaller()
    project = config_reader.read()
    installer.install(project.name, project.install)
