from __future__ import annotations

from os import linesep
from textwrap import wrap

import click
from attrs import define, field
from cloudshell.rest.exceptions import FeatureUnavailable
from requests.exceptions import SSLError
from terminaltables import AsciiTable

from ..exceptions import FatalError

from shellfoundry.constants import ALTERNATIVE_TEMPLATES_PATH
from shellfoundry.utilities.config_reader import (
    CloudShellConfigReader,
    Configuration,
    ShellFoundryConfig,
)
from shellfoundry.utilities.standards.standards_retriever import Standards
from shellfoundry.utilities.template_retriever import (
    FilteredTemplateRetriever,
    TemplateRetriever,
)


@define
class ListCommandExecutor:
    default_view: str | None = field(default=None)
    template_retriever: FilteredTemplateRetriever = field(default=None)
    standards: Standards = field(factory=Standards)
    cloudshell_config_reader: Configuration = field(
        init=False, factory=lambda: Configuration(CloudShellConfigReader())
    )
    show_info_msg: bool = field(init=False)

    def __attrs_post_init__(self):
        self.show_info_msg = self.default_view is None

        if not self.default_view:
            self.default_view = Configuration(ShellFoundryConfig()).read().defaultview

        if not self.template_retriever:
            self.template_retriever = FilteredTemplateRetriever(
                self.default_view, TemplateRetriever()
            )

    def list(self):  # noqa: A003
        online_mode = self.cloudshell_config_reader.read().online_mode.lower() == "true"
        template_location = self.cloudshell_config_reader.read().template_location

        try:
            standards = self.standards.fetch()
            if online_mode:
                try:
                    templates = self.template_retriever.get_templates(
                        standards=standards
                    )
                except SSLError:
                    raise click.UsageError(
                        "Could not retrieve the templates list. Are you offline?"
                    )
            else:
                templates = self.template_retriever.get_templates(
                    template_location=template_location, standards=standards
                )
        except FatalError as err:
            raise click.UsageError(str(err))
        except FeatureUnavailable:
            if online_mode:
                templates = self.template_retriever.get_templates(
                    alternative=ALTERNATIVE_TEMPLATES_PATH
                )
            else:
                templates = self.template_retriever.get_templates(
                    template_location=template_location
                )

        if not templates:
            raise click.ClickException(
                "No templates matched the view criteria(gen1/gen2) or "
                "available templates and standards are not compatible"
            )

        template_rows = [["Template Name", "CloudShell Ver.", "Description"]]
        for template in list(templates.values()):
            template = template[0]
            cs_ver_txt = f"{str(template.min_cs_ver)} and up"
            template_rows.append(
                [template.name, cs_ver_txt, template.description]
            )  # description is later wrapped based on the size of the console

        table = AsciiTable(template_rows)
        table.outer_border = False
        table.inner_column_border = False
        max_width = table.column_max_width(2)

        if max_width <= 0:  # verify that the console window is not too small,
            # and if so skip the wrapping logic
            click.echo(table.table)
            return

        row = 1
        for template in list(templates.values()):
            template = template[0]
            wrapped_string = linesep.join(wrap(template.description, max_width))
            table.table_data[row][2] = wrapped_string
            row += 1

        output = table.table
        click.echo(output)

        if self.show_info_msg:
            click.echo(
                """
As of CloudShell 8.0, CloudShell uses 2nd generation shells,
to view the list of 1st generation shells use: shellfoundry list --gen1.
For more information, please visit our devguide:
https://help.quali.com/devguide
"""
            )
