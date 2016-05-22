import unittest
import mock
from shellfoundry.utilities.template_retriever import TemplateRetriever


class TestTemplateRetriever(unittest.TestCase):
    def mock_get_templates_from_github(self):
        return """
        templates:
          - name : switch
            description : Basic switch template
            repository : https://github.com/QualiSystems/shellfoundry-switch-template
          - name : router
            description : Basic router template
            repository : https://github.com/QualiSystems/shellfoundry-router-template
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
