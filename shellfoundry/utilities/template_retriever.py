import requests
import yaml
from collections import OrderedDict

from shellfoundry.models.shell_template import ShellTemplate
from .filters import CompositeFilter

TEMPLATES_YML = 'https://raw.github.com/QualiSystems/shellfoundry/master/templates_0.2.0.yml'


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
                template['min_cs_ver'],
                template['params'])

        return templatesdic

    @staticmethod
    def _get_templates_from_github():
        session = requests.Session()
        session.mount('https://', requests.adapters.HTTPAdapter(max_retries=5))
        return session.get(TEMPLATES_YML).text


class FilteredTemplateRetriever(object):
    def __init__(self, template_type, template_retriever=None):
        self.template_retriever = template_retriever or TemplateRetriever()
        self.filter = CompositeFilter(template_type).filter

    def get_templates(self):
        templates = self.template_retriever.get_templates()
        return OrderedDict((k, v) for k, v in templates.iteritems() if self.filter(k))
