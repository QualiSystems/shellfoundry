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
        session = requests.Session()
        session.mount('https://', requests.adapters.HTTPAdapter(max_retries=5))
        return session.get(TEMPLATES_YML).text


class FilteredTemplateRetriever(object):
    def __init__(self, template_type, template_retriever=None):
        self.template_type = template_type
        self.template_retriever = template_retriever or TemplateRetriever()

    def get_templates(self):
        templates = self.template_retriever.get_templates()
        if self.template_type is None or self.template_type == 'all':
            return templates
        return OrderedDict((k, v) for k, v in templates.iteritems() if self._filter(k))

    def _filter(self, template_name):
        if self.template_type == 'tosca':
            return self._filter_out_legacy_template(template_name)
        return self._filter_out_tosca_template(template_name)

    def _filter_out_legacy_template(self, template_name):
        return 'tosca' in template_name

    def _filter_out_tosca_template(self, template_name):
        return not self._filter_out_legacy_template(template_name)
