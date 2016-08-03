import os
import click
from cookiecutter.main import cookiecutter
from shellfoundry.utilities.repository_downloader import RepositoryDownloader
from shellfoundry.utilities.temp_dir_context import TempDirContext
from shellfoundry.utilities.template_retriever import TemplateRetriever


class NewCommandExecutor(object):
    def __init__(self, template_retriever=None, repository_downloader=None):
        self.template_retriever = template_retriever or TemplateRetriever()
        self.repository_downloader = repository_downloader or RepositoryDownloader()

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
        template_obj = templates[template]

        with TempDirContext(name) as temp_dir:

            repo_path = self.repository_downloader.download_template(temp_dir, template_obj.repository)
            # Supports creating shell in the same directory
            if name == '.':
                template_obj.params['project_name'] = os.path.split(os.getcwd())[1]
                cookiecutter(repo_path, no_input=True,
                             extra_context=template_obj.params,
                             overwrite_if_exists=True, output_dir='..')
            else:
                print name
                template_obj.params['project_name'] = name
                cookiecutter(repo_path, no_input=True,
                             extra_context=template_obj.params)

    @staticmethod
    def _get_templates_with_comma(templates):
        return ', '.join(templates.keys())
