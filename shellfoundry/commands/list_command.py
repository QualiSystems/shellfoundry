import click
import textwrap

from requests.exceptions import SSLError
from shellfoundry.utilities.template_retriever import TemplateRetriever
from terminaltables import AsciiTable
from textwrap import wrap

class ListCommandExecutor(object):
    def __init__(self, template_retriever=None):
        self.template_retriever = template_retriever or TemplateRetriever()

    def list(self):
        try:
            templates = self.template_retriever.get_templates()
        except SSLError:
            raise click.UsageError('Could not retrieve the templates list. Are you offline?')

        template_rows = [['Template Name','Description']]
        for template in templates.values():
            template_rows.append([template.name, '']) #description is added later by column max width

        table = AsciiTable(template_rows)
        table.outer_border = False
        table.inner_column_border = False
        max_width = table.column_max_width(1)
        row = 1
        for template in templates.values():
            wrapped_string = '\n'.join(wrap(template.description, max_width))
            table.table_data[row][1] = wrapped_string
            row += 1

        output = table.table
        click.echo(output)
