import requests
import yaml

TEMPLATES_YML = 'https://raw.github.com/QualiSystems/shellfoundry/master/templates.yml'


class TemplateRetriever(object):
    def get_templates(self):
        response = self._get_templates_from_github()
        config = yaml.load(response)
        if not config or 'templates' not in config:
            return []

        return config['templates']

    @staticmethod
    def _get_templates_from_github():
        return requests.get(TEMPLATES_YML).text
