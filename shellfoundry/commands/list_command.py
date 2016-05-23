import click

from shellfoundry.utilities.template_retriever import TemplateRetriever


class ListCommandExecutor(object):
    def __init__(self, template_retriever=None):
        self.template_retriever = template_retriever or TemplateRetriever()

    def list(self):
        templates = self.template_retriever.get_templates()
        click.echo(u'Supported templates are:\r\n{0}'.format('\r\n'.join(
            [template.name + ': ' + template.description for template in templates.values()]
        )))
