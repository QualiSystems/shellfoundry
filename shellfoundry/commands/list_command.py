import click
import shellfoundry

from os import linesep, path
from requests.exceptions import SSLError
from shellfoundry.utilities.template_retriever import TemplateRetriever, FilteredTemplateRetriever
from shellfoundry.utilities.config_reader import Configuration, ShellFoundryConfig
from shellfoundry.utilities.standards.standards_filter import StandardsFilter
from shellfoundry.utilities.cloudshell_api import CloudShellClient
from ..exceptions import FatalError
from cloudshell.rest.exceptions import FeatureUnavailable
from terminaltables import AsciiTable
from textwrap import wrap

ALTERNATIVE_TEMPLATES_PATH = path.join(path.dirname(shellfoundry.__file__), 'data', 'templates.yml')


class ListCommandExecutor(object):
    def __init__(self, default_view=None, template_retriever=None):
        dv = default_view or Configuration(ShellFoundryConfig()).read().defaultview
        self.template_retriever = template_retriever or FilteredTemplateRetriever(dv, TemplateRetriever())
        self.show_info_msg = default_view is None
        self._cloudshell = CloudShellClient()

    def list(self):
        cs_client = self._create_cloudshell_client()

        try:
            standards = cs_client.get_installed_standards()
            templates = StandardsFilter().filter(standards, self.template_retriever.get_templates())
        except SSLError:
            raise click.UsageError('Could not retrieve the templates list. Are you offline?')
        except FeatureUnavailable:
            templates = self.template_retriever.get_templates(alternative=ALTERNATIVE_TEMPLATES_PATH)

        if not templates:
            click.echo('No templates matched the criteria')
            return

        template_rows = [['Template Name', 'CloudShell Ver.', 'Description']]
        for template in templates.values():
            cs_ver_txt = str(template.min_cs_ver) + " and up"
            template_rows.append(
                [template.name, cs_ver_txt,
                 template.description])  # description is later wrapped based on the size of the console

        table = AsciiTable(template_rows)
        table.outer_border = False
        table.inner_column_border = False
        max_width = table.column_max_width(2)

        if max_width <= 0:  # verify that the console window is not too small, and if so skip the wrapping logic
            click.echo(table.table)
            return

        row = 1
        for template in templates.values():
            wrapped_string = linesep.join(wrap(template.description, max_width))
            table.table_data[row][2] = wrapped_string
            row += 1

        output = table.table
        click.echo(output)

        if self.show_info_msg:
            click.echo('''
As of CloudShell 8.0, CloudShell uses 2nd generation shells, to view the list of 1st generation shells use: shellfoundry list --gen1.
For more information, please visit our devguide: https://qualisystems.github.io/devguide/''')

    def _create_cloudshell_client(self):
        try:
            cs_client = self._cloudshell.create_client()
        except FatalError:
            raise click.UsageError('Could not retrieve the templates list. Are you offline?')
        return cs_client
