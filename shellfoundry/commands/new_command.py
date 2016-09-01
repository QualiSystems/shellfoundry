import os
import click
from cookiecutter.main import cookiecutter
from requests.exceptions import SSLError
from shellfoundry.utilities.cookiecutter_integration import CookiecutterTemplateCompiler
from shellfoundry.utilities.repository_downloader import RepositoryDownloader
from shellfoundry.utilities.temp_dir_context import TempDirContext
from shellfoundry.utilities.template_retriever import TemplateRetriever


class NewCommandExecutor(object):
    LOCAL_TEMPLATE_URL_PREFIX = 'local:'

    def __init__(self, template_compiler=None, template_retriever=None, repository_downloader=None):
        self.template_retriever = template_retriever or TemplateRetriever()
        self.repository_downloader = repository_downloader or RepositoryDownloader()
        self.template_compiler = template_compiler or CookiecutterTemplateCompiler()

    def new(self, name, template):
        """
        Create a new shell based on a template.
        :param str name: The name of the Shell
        :param str template: The name of the template to use
        """

        # Special handling for the case where the user runs 'shellfoundry .' in such a case the '.'
        # character is substituted for the shell name and the content of the current folder is populated
        running_on_same_folder = False
        if name == os.path.curdir:
            name = os.path.split(os.getcwd())[1]
            running_on_same_folder = True

        if self._is_local_template(template):
            self._import_local_template(name, running_on_same_folder, template)

        else:
            self._import_online_template(name, running_on_same_folder, template)

        click.echo('Created shell {0} based on template {1}'.format(name, template))

    def _import_online_template(self, name, running_on_same_folder, template):
        # Create a temp folder for the operation to make sure we delete it after
        with TempDirContext(name) as temp_dir:

            try:
                templates = self.template_retriever.get_templates()
            except SSLError:
                raise click.UsageError("Cannot retrieve templates list, are you offline?")

            if template not in templates:
                raise click.BadParameter(
                    u'Template {0} does not exist. Supported templates are: {1}'.format(template,
                                                                                        self._get_templates_with_comma(
                                                                                            templates)))
            template_obj = templates[template]

            repo_path = self.repository_downloader.download_template(temp_dir, template_obj.repository)

            self.template_compiler.compile_template(name, repo_path, template_obj.params,
                                                    running_on_same_folder)

    def _import_local_template(self, name, running_on_same_folder, template):
        repo_path = self._remove_prefix(template, NewCommandExecutor.LOCAL_TEMPLATE_URL_PREFIX)

        if not os.path.exists(repo_path) or not os.path.isdir(repo_path):
            raise click.BadParameter("Could not locate a template folder at: {template_path}"
                                     .format(template_path=repo_path))

        self.template_compiler.compile_template(shell_name=name, template_path=repo_path, extra_context={},
                                                running_on_same_folder=running_on_same_folder)

    def _is_local_template(self, template):
        return template.startswith(NewCommandExecutor.LOCAL_TEMPLATE_URL_PREFIX)

    def _remove_prefix(self, string, prefix):
        return string.rpartition(prefix)[-1]

    @staticmethod
    def _get_templates_with_comma(templates):
        return ', '.join(templates.keys())
