import click
from cookiecutter.main import cookiecutter

from shellfoundry.template_retriever import TemplateRetriever


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

        cookiecutter(templates[template], no_input=True, extra_context={u'project_name': name})

    @staticmethod
    def _get_templates_with_comma(templates):
        return ', '.join(templates.keys())
