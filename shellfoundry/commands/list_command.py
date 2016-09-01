import click
import textwrap

from requests.exceptions import SSLError
from shellfoundry.utilities.template_retriever import TemplateRetriever


class ListCommandExecutor(object):
    def __init__(self, template_retriever=None):
        self.template_retriever = template_retriever or TemplateRetriever()

    def list(self):
        try:
            templates = self.template_retriever.get_templates()
        except SSLError:
            raise click.UsageError('Could not retrieve the templates list. Are you offline?')

        prefixlen = 23
        output = u'\r\nTemplates:\r\n'
        for template in templates.values():
            prefix = ("  " + template.name + " ").ljust(prefixlen)
            wrapper = textwrap.TextWrapper(initial_indent=prefix, width=77,
                                           subsequent_indent=' ' * prefixlen)
            message = template.description
            output += '\r\n' + wrapper.fill(message)

        click.echo(output)
