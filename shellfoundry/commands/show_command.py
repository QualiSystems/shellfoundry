from __future__ import annotations

import click
import requests
from attrs import define, field

from shellfoundry.constants import MASTER_BRANCH_NAME
from shellfoundry.exceptions import NoVersionsHaveBeenFoundException
from shellfoundry.utilities.filters import GEN_TWO_FILTER
from shellfoundry.utilities.template_retriever import (
    FilteredTemplateRetriever,
    TemplateRetriever,
)
from shellfoundry.utilities.template_versions import TemplateVersions


@define
class ShowCommandExecutor:
    template_retriever: FilteredTemplateRetriever = field(
        factory=lambda: FilteredTemplateRetriever(GEN_TWO_FILTER, TemplateRetriever())
    )

    def show(self, template_name: str) -> None:
        """Show all template versions based on provided template name."""
        try:
            template_repo = self.template_retriever.get_templates()[template_name][
                0
            ].repository  # noqa: E501
        except Exception:
            raise click.ClickException(
                f"The template '{template_name}' does not exist, "
                f"please specify a valid 2nd Gen shell template."
            )

        if not template_repo:
            raise click.ClickException("Repository url is empty")

        try:
            branches = TemplateVersions(
                *template_repo.split("/")[-2:]
            ).get_versions_of_template()
        except (requests.RequestException, NoVersionsHaveBeenFoundException) as ex:
            raise click.ClickException(str(ex))
        branches.remove(MASTER_BRANCH_NAME)
        if not TemplateVersions.has_versions(
            branches
        ):  # validating that besides master there are other versions
            raise click.ClickException("No versions have been found for this template")
        self.mark_latest(branches)
        for branch_name in branches:
            click.echo(branch_name)

    @staticmethod
    def mark_latest(branches: list[str]) -> None:
        branches[0] = f"{branches[0]} (latest)"
