import click
import textwrap

from shellfoundry.utilities.template_retriever import TemplateRetriever


class ListCommandExecutor(object):
    def __init__(self, template_retriever=None):
        self.template_retriever = template_retriever or TemplateRetriever()

    def list(self):
        templates = self.template_retriever.get_templates()
        prefixlen = 23
        output = u'\r\nSupported templates are:\r\n'
        for template in templates.values():
            prefix = (" " + template.name + ": ").ljust(prefixlen)
            wrapper = textwrap.TextWrapper(initial_indent=prefix, width=77,
                                           subsequent_indent=' ' * prefixlen)
            message = template.description
            output += '\r\n' + wrapper.fill(message)

        click.echo(output)
