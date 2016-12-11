import click
import textwrap

from os import linesep
from requests.exceptions import SSLError
from shellfoundry.utilities.template_retriever import TemplateRetriever, FilteredTemplateRetriever
from shellfoundry.utilities.config_reader import Configuration, ShellFoundryConfig
from terminaltables import AsciiTable
from textwrap import wrap

class ListCommandExecutor(object):
    def __init__(self, default_view=None, template_retriever=None):
        default_view = default_view or Configuration(ShellFoundryConfig()).read().defaultview
        self.template_retriever = template_retriever or FilteredTemplateRetriever(default_view, TemplateRetriever())

    def list(self):
        try:
            templates = self.template_retriever.get_templates()
        except SSLError:
            raise click.UsageError('Could not retrieve the templates list. Are you offline?')

        if not templates:
            click.echo('No templates matched the criteria')
            return

        template_rows = [['Template Name','Description']]
        for template in templates.values():
            template_rows.append(
                [template.name, template.description])  # description is later wrapped based on the size of the console

        table = AsciiTable(template_rows)
        table.outer_border = False
        table.inner_column_border = False
        max_width = table.column_max_width(1)

        if max_width <= 0: # verify that the console window is not too small, and if so skip the wrapping logic
            click.echo(table.table)
            return

        row = 1
        for template in templates.values():
            wrapped_string = linesep.join(wrap(template.description, max_width))
            table.table_data[row][1] = wrapped_string
            row += 1

        output = table.table
        click.echo(output)
