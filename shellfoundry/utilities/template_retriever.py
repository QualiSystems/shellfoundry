import requests
import yaml
from collections import OrderedDict

from shellfoundry.models.shell_template import ShellTemplate

TEMPLATES_YML = 'https://raw.github.com/QualiSystems/shellfoundry/master/templates.yml'


class TemplateRetriever(object):

    def get_templates(self):
        """
        :return: Dictionary of shellfoundry.ShellTemplate
        """
        response = self._get_templates_from_github()
        config = yaml.load(response)
        if not config or 'templates' not in config:
            return []

        templatesdic = OrderedDict()
        for template in config['templates']:
            templatesdic[template['name']] = ShellTemplate(
                template['name'],
                template['description'],
                template['repository'],
                template['params'])

        return templatesdic

    @staticmethod
    def _get_templates_from_github():
        return requests.get(TEMPLATES_YML).text
