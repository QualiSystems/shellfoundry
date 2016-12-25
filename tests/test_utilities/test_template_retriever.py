import unittest
import mock
import httpretty
from shellfoundry.utilities.template_retriever import TemplateRetriever, TEMPLATES_YML


class TestTemplateRetriever(unittest.TestCase):
    @staticmethod
    def mock_get_templates_from_github():
        return """
        templates:
          - name : switch
            description : Basic switch template
            repository : https://github.com/QualiSystems/shellfoundry-switch-template
            params:
                project_name:
          - name : router
            description : Basic router template
            repository : https://github.com/QualiSystems/shellfoundry-router-template
            params:
                project_name:
        """

    @mock.patch('shellfoundry.utilities.template_retriever.TemplateRetriever._get_templates_from_github',
                mock_get_templates_from_github)
    def test_get_templates(self):
        # Arrange
        template_retriever = TemplateRetriever()

        # Act
        templates = template_retriever.get_templates()

        # Assert
        self.assertEqual(templates['router'].name, 'router')
        self.assertEqual(templates['router'].description, 'Basic router template')
        self.assertEqual(templates['router'].repository, 'https://github.com/QualiSystems/shellfoundry-router-template')

        self.assertEqual(templates['switch'].name, 'switch')
        self.assertEqual(templates['switch'].description, 'Basic switch template')
        self.assertEqual(templates['switch'].repository, 'https://github.com/QualiSystems/shellfoundry-switch-template')

    @mock.patch('shellfoundry.utilities.template_retriever.TemplateRetriever._get_templates_from_github',
                lambda x: "")
    def test_empty_templates_should_return_when_not_templates_found_on_github(self):
        # Arrange
        template_retriever = TemplateRetriever()

        # Act
        templates = template_retriever.get_templates()

        # Assert
        self.assertEqual(templates, [])

    @httpretty.activate
    def test_session_max_retires(self):
        # Arrange
        template_retriever = TemplateRetriever()

        httpretty.register_uri('GET', TEMPLATES_YML, body=self.mock_get_templates_from_github())

        # Act
        templates = template_retriever.get_templates()

        # Assert
        self.assertEqual(templates['router'].name, 'router')
        self.assertEqual(templates['router'].description, 'Basic router template')
        self.assertEqual(templates['router'].repository, 'https://github.com/QualiSystems/shellfoundry-router-template')

        self.assertEqual(templates['switch'].name, 'switch')
        self.assertEqual(templates['switch'].description, 'Basic switch template')
        self.assertEqual(templates['switch'].repository, 'https://github.com/QualiSystems/shellfoundry-switch-template')
