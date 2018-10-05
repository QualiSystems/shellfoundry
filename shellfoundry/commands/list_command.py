#!/usr/bin/python
# -*- coding: utf-8 -*-

import click

from os import linesep
from requests.exceptions import SSLError
from terminaltables import AsciiTable
from textwrap import wrap

from cloudshell.rest.exceptions import FeatureUnavailable
from shellfoundry import ALTERNATIVE_TEMPLATES_PATH, ALTERNATIVE_STANDARDS_PATH
from shellfoundry.utilities.template_retriever import TemplateRetriever, FilteredTemplateRetriever
from shellfoundry.utilities.config_reader import Configuration, ShellFoundryConfig, CloudShellConfigReader
from shellfoundry.utilities.standards import StandardVersionsFactory, Standards
from ..exceptions import FatalError
from shellfoundry.utilities.template_url import construct_template_url


class ListCommandExecutor(object):
    def __init__(self, default_view=None, template_retriever=None, standards=None, offline_links=None, standard_versions=None):
        """

        :param str default_view:
        :param template_retriever:
        :param Standards standards:
        :param offline_links:
        :param StandardVersions standard_versions:
        """
        dv = default_view or Configuration(ShellFoundryConfig()).read().defaultview
        self.template_retriever = template_retriever or FilteredTemplateRetriever(dv, TemplateRetriever())
        self.show_info_msg = default_view is None
        self.standards = standards or Standards()
        self.get_offline_links = offline_links is not None
        self.cloudshell_config_reader = Configuration(CloudShellConfigReader())
        self.standard_versions = standard_versions or StandardVersionsFactory()

    def _get_template_latest_version(self, standards_list, standard):
        try:
            return self.standard_versions.create(standards_list).get_latest_version(standard)
        except Exception as e:
            click.ClickException(e.message)

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
            standards = self.standards.fetch(alternative=ALTERNATIVE_STANDARDS_PATH)
            if online_mode:
                templates = self.template_retriever.get_templates(alternative=ALTERNATIVE_TEMPLATES_PATH)
            else:
                templates = self.template_retriever.get_templates(template_location=template_location)

        if not templates:
            raise click.ClickException("No templates matched the view criteria(gen1/gen2) or "
                                       "available templates and standards are not compatible")

        if self.get_offline_links:
            template_rows = [["Template Name", "Download URL"]]
            for template in templates.values():
                template = template[0]
                version = self._get_template_latest_version(standards, template.standard)
                url = construct_template_url(template.repository, version)
                template_rows.append([template.name, url])  # description is later wrapped based on the size of the console

            table = AsciiTable(template_rows)
            table.outer_border = False
            table.inner_column_border = False
            max_width = table.column_max_width(1)

            if max_width <= 0:  # verify that the console window is not too small, and if so skip the wrapping logic
                click.echo(table.table)
                return

            row = 0
            for template, url in template_rows:
                if row > 0:
                    wrapped_string = linesep.join(wrap(url, max_width))
                    table.table_data[row][1] = wrapped_string
                row += 1

            output = table.table
            click.echo(output)

        else:
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
As of CloudShell 8.0, CloudShell uses 2nd generation shells. To view the list of the 1st generation shells use: shellfoundry list --gen1.
For more information, please visit our dev guide at: https://devguide.quali.com""")
