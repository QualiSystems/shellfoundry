import click
import requests
import shellfoundry.exceptions as exc

from shellfoundry import MASTER_BRANCH_NAME
from shellfoundry.utilities import GEN_TWO_FILTER
from shellfoundry.utilities.template_retriever import TemplateRetriever, FilteredTemplateRetriever
from shellfoundry.utilities.template_versions import TemplateVersions

LATEST_STAMP = '{} (latest)'


class ShowCommandExecutor(object):
    def __init__(self, template_retriever=None):
        self.template_retriever = template_retriever or FilteredTemplateRetriever(GEN_TWO_FILTER, TemplateRetriever())

    def show(self, template_name):
        try:
            template_repo = self.template_retriever.get_templates()[template_name].repository
        except:
            raise click.ClickException(
                "The template '{}' does not exist, please specify a valid 2nd Gen shell template.".format(
                    template_name))

        if not template_repo:
            raise click.ClickException('Repository url is empty')

        try:
            branches = TemplateVersions(*template_repo.split('/')[-2:]).get_versions_of_template()
        except (requests.RequestException, exc.NoVersionsHaveBeenFoundException) as ex:
            raise click.ClickException(ex.message)
        branches.remove(MASTER_BRANCH_NAME)
        if not TemplateVersions.has_versions(branches):  # validating that besides master there are other versions
            raise click.ClickException("No versions have been found for this template")
        self.mark_latest(branches)
        for branch_name in branches:
            click.echo(branch_name)

    def mark_latest(self, branches):
        branches[0] = LATEST_STAMP.format(branches[0])
