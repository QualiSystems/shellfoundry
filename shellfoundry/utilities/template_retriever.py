import requests
import yaml
from collections import OrderedDict

from shellfoundry.models.shell_template import ShellTemplate
from .filters import CompositeFilter
from .standards import trim_standard, STANDARD_NAME_KEY
from shellfoundry.utilities import GEN_TWO, SEPARATOR

TEMPLATES_YML = 'https://raw.github.com/QualiSystems/shellfoundry/master/templates_v1.yml'


class TemplateRetriever(object):
    def get_templates(self, **kwargs):
        """
        :return: Dictionary of shellfoundry.ShellTemplate
        """

        alternative_path = kwargs.get('alternative', None)
        standards = kwargs.get('standards', [])

        if alternative_path:
            response = self._get_templates_from_path(alternative_path)
        else:
            response = self._get_templates_from_github()

        config = yaml.load(response)
        if not config or 'templates' not in config:
            return {}

        templatesdic = OrderedDict()
        for template in config['templates']:
            templatesdic[template['name']] = ShellTemplate(
                template['name'],
                template['description'],
                template['repository'],
                template['min_cs_ver'],
                self._get_standard_out_of_name(template['name']),
                template['params'])

        return self._filter_by_standards(templatesdic, standards)

    @staticmethod
    def _get_templates_from_github():
        session = requests.Session()
        session.mount('https://', requests.adapters.HTTPAdapter(max_retries=5))
        return session.get(TEMPLATES_YML).text

    @staticmethod
    def _get_templates_from_path(alternative_path):
        with open(alternative_path, mode='r') as stream:
            response = stream.read()
        return response

    @staticmethod
    def _get_standard_out_of_name(template_name, default=None):
        """
        :type template_name str
        :return:
        """
        type_index = 0
        standard_index = 1
        template = template_name.split(SEPARATOR)
        if template[type_index] != GEN_TWO:
            return default
        return template[standard_index]

    @staticmethod
    def _filter_by_standards(templates, standards):
        """
        :type templates collections.OrderedDict
        :type standards list
        :return:
        """
        if not standards:
            return templates

        trimmed_standards = [trim_standard(standard[STANDARD_NAME_KEY]) for standard in standards]
        template_names = [x.name for x in templates.itervalues() if not x.standard or x.standard in trimmed_standards]  # creates a list of all matching templates names by available standard

        return OrderedDict((name, templates[name]) for name in template_names)


class FilteredTemplateRetriever(object):
    def __init__(self, template_type, template_retriever=None):
        self.template_retriever = template_retriever or TemplateRetriever()
        self.filter = CompositeFilter(template_type).filter

    def get_templates(self, **kwargs):
        templates = self.template_retriever.get_templates(**kwargs)
        return OrderedDict((k, v) for k, v in templates.iteritems() if self.filter(k))
