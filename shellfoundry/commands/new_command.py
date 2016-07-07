import os

import click
from cookiecutter.main import cookiecutter

from shellfoundry.utilities.template_retriever import TemplateRetriever


class NewCommandExecutor(object):
    def __init__(self, template_retriever=None):
        self.template_retriever = template_retriever or TemplateRetriever()

    def new(self, name, template):
        """
        Create a new shell based on a template.
        :param name:
        :param template:
        """
        templates = self.template_retriever.get_templates()

        if template not in templates:
            raise click.BadParameter(
                u'Template {0} does not exist. Supported templates are: {1}'.format(template,
                                                                                    self._get_templates_with_comma(
                                                                                        templates)))
        # Supports creating shell in the same directory
        if name == '.':
            shell_name = os.path.split(os.getcwd())[1]
            cookiecutter(templates[template].repository, no_input=True, extra_context={u'project_name': shell_name},
                         overwrite_if_exists=True, output_dir='..')
        else:
            cookiecutter(templates[template].repository, no_input=True, extra_context={u'project_name': name})

    @staticmethod
    def _get_templates_with_comma(templates):
        return ', '.join(templates.keys())
