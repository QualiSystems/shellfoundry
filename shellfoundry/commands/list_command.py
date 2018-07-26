#!/usr/bin/python
# -*- coding: utf-8 -*-

import click

from os import linesep
from requests.exceptions import SSLError
from shellfoundry import ALTERNATIVE_TEMPLATES_PATH
from shellfoundry.utilities.template_retriever import TemplateRetriever, FilteredTemplateRetriever
from shellfoundry.utilities.config_reader import Configuration, ShellFoundryConfig, CloudShellConfigReader
from shellfoundry.utilities.standards import Standards
from ..exceptions import FatalError
from cloudshell.rest.exceptions import FeatureUnavailable
from terminaltables import AsciiTable
from textwrap import wrap


class ListCommandExecutor(object):
    def __init__(self, default_view=None, template_retriever=None, standards=None):
        """
        :param str default_view:
        :param Standards standards:
        """
        dv = default_view or Configuration(ShellFoundryConfig()).read().defaultview
        self.template_retriever = template_retriever or FilteredTemplateRetriever(dv, TemplateRetriever())
        self.show_info_msg = default_view is None
        self.standards = standards or Standards()
        self.cloudshell_config_reader = Configuration(CloudShellConfigReader())

    def list(self):
        """  """

        online_mode = self.cloudshell_config_reader.read().online_mode.lower() == "true"
        template_location = self.cloudshell_config_reader.read().template_location

        try:
            standards = self.standards.fetch()
            if online_mode:
                try:
                    templates = self.template_retriever.get_templates(standards=standards)
                except SSLError:
                    raise click.UsageError("Could not retrieve the templates list. Are you offline?")
            else:
                templates = self.template_retriever.get_templates(template_location=template_location,
                                                                  standards=standards)
        except FatalError as err:
            raise click.UsageError(err.message)
        except FeatureUnavailable:
            if online_mode:
                templates = self.template_retriever.get_templates(alternative=ALTERNATIVE_TEMPLATES_PATH)
            else:
                templates = self.template_retriever.get_templates(template_location=template_location)

        if not templates:
            raise click.ClickException("No templates matched the criteria")

        template_rows = [["Template Name", "CloudShell Ver.", "Description"]]
        for template in templates.values():
            template = template[0]
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
            template = template[0]
            wrapped_string = linesep.join(wrap(template.description, max_width))
            table.table_data[row][2] = wrapped_string
            row += 1

        output = table.table
        click.echo(output)

        if self.show_info_msg:
            click.echo("""
As of CloudShell 8.0, CloudShell uses 2nd generation shells, to view the list of 1st generation shells use: shellfoundry list --gen1.
For more information, please visit our devguide: https://qualisystems.github.io/devguide/""")
