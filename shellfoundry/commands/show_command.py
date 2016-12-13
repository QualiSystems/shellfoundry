import click
import requests
import ast

from shellfoundry.utilities.template_retriever import TemplateRetriever, FilteredTemplateRetriever


VERSIONS_URL = 'https://api.github.com/repos/{}/{}/branches'
NAME_PLACEHOLDER = 'name'
MASTER_BRANCH_NAME = 'master'
LATEST_STAMP = '{} (latest)'


class ShowCommandExecutor(object):
    def __init__(self, template_retriever=None):
        self.template_retriever = template_retriever or FilteredTemplateRetriever('tosca', TemplateRetriever())

    def show(self, template_name):
        try:
            template_repo = self.template_retriever.get_templates()[template_name].repository
        except:
            raise click.ClickException('Template does not exist')

        if not template_repo:
            raise click.ClickException('Repository url is empty')

        request = requests.get(VERSIONS_URL.format(*template_repo.split('/')[-2:]))

        if request.status_code != requests.codes.ok:
            raise click.ClickException('Failed to receive versions from host')

        request_arr = ast.literal_eval(request.text)

        branches = [d[NAME_PLACEHOLDER] for d in request_arr]
        branches.remove(MASTER_BRANCH_NAME)
        branches.sort(reverse=True)
        self.validate_has_versions(branches)
        self.mark_latest(branches)

        for branch_name in branches:
            click.echo(branch_name)

    def mark_latest(self, branches):
        branches[0] = LATEST_STAMP.format(branches[0])

    def validate_has_versions(self, branches):
        first_branch = next(iter(branches or []), None)
        if first_branch is None:
            raise click.ClickException("No versions has been found for this template")
