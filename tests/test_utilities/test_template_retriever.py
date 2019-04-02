import unittest
import mock
import httpretty
import pyfakefs.fake_filesystem_unittest

from shellfoundry.utilities import GEN_ONE, GEN_TWO, NO_FILTER
from shellfoundry.utilities.template_retriever import TemplateRetriever, FilteredTemplateRetriever, TEMPLATES_YML


class TestTemplateRetriever(unittest.TestCase):
    @staticmethod
    def mock_get_templates_from_github():
        return """
        templates:
          - name : gen1/switch
            description : Basic switch template
            repository : https://github.com/QualiSystems/shellfoundry-switch-template
            params:
                project_name:
            min_cs_ver: 7.0
          - name : gen1/router
            description : Basic router template
            repository : https://github.com/QualiSystems/shellfoundry-router-template
            params:
                project_name:
            min_cs_ver: 7.0
          - name : gen2/switch
            description : Basic switch template
            repository : https://github.com/QualiSystems/shellfoundry-switch-template
            params:
                project_name:
            min_cs_ver: 8.0
          - name : gen2/software-asset
            description : Basic software-asset template
            repository : https://github.com/QualiSystems/shellfoundry-software-asset-template
            params:
                project_name:
            min_cs_ver: 8.0
        """

    @mock.patch('shellfoundry.utilities.template_retriever.TemplateRetriever._get_templates_from_github',
                mock_get_templates_from_github)
    def test_get_templates(self):
        # Arrange
        template_retriever = TemplateRetriever()

        # Act
        templates = template_retriever.get_templates()

        # Assert
        self.assertEqual(templates['gen1/router'][0].name, 'gen1/router')
        self.assertEqual(templates['gen1/router'][0].description, 'Basic router template')
        self.assertEqual(templates['gen1/router'][0].repository, 'https://github.com/QualiSystems/shellfoundry-router-template')

        self.assertEqual(templates['gen1/switch'][0].name, 'gen1/switch')
        self.assertEqual(templates['gen1/switch'][0].description, 'Basic switch template')
        self.assertEqual(templates['gen1/switch'][0].repository, 'https://github.com/QualiSystems/shellfoundry-switch-template')

    @mock.patch('shellfoundry.utilities.template_retriever.TemplateRetriever._get_templates_from_github',
                lambda x: "")
    def test_empty_templates_should_return_when_not_templates_found_on_github(self):
        # Arrange
        template_retriever = TemplateRetriever()

        # Act
        templates = template_retriever.get_templates()

        # Assert
        self.assertEqual(templates, {})

    @httpretty.activate
    def test_session_max_retires(self):
        # Arrange
        template_retriever = TemplateRetriever()

        httpretty.register_uri('GET', TEMPLATES_YML, body=self.mock_get_templates_from_github())

        # Act
        templates = template_retriever.get_templates()

        # Assert
        self.assertEqual(templates['gen1/router'][0].name, 'gen1/router')
        self.assertEqual(templates['gen1/router'][0].description, 'Basic router template')
        self.assertEqual(templates['gen1/router'][0].repository, 'https://github.com/QualiSystems/shellfoundry-router-template')

        self.assertEqual(templates['gen1/switch'][0].name, 'gen1/switch')
        self.assertEqual(templates['gen1/switch'][0].description, 'Basic switch template')
        self.assertEqual(templates['gen1/switch'][0].repository, 'https://github.com/QualiSystems/shellfoundry-switch-template')

    @httpretty.activate
    def test_filtered_template_retriever_gen1_success(self):
        # Arrange
        template_retriever = FilteredTemplateRetriever(GEN_ONE, TemplateRetriever())

        httpretty.register_uri('GET', TEMPLATES_YML, body=self.mock_get_templates_from_github())

        # Act
        templates = template_retriever.get_templates()

        # Assert
        self.assertEqual(len(templates), 2)
        self.assertEqual(templates['gen1/router'][0].name, 'gen1/router')
        self.assertEqual(templates['gen1/router'][0].description, 'Basic router template')
        self.assertEqual(templates['gen1/router'][0].repository, 'https://github.com/QualiSystems/shellfoundry-router-template')

        self.assertEqual(templates['gen1/switch'][0].name, 'gen1/switch')
        self.assertEqual(templates['gen1/switch'][0].description, 'Basic switch template')
        self.assertEqual(templates['gen1/switch'][0].repository, 'https://github.com/QualiSystems/shellfoundry-switch-template')

    @httpretty.activate
    def test_filtered_template_retriever_gen2_success(self):
        # Arrange
        template_retriever = FilteredTemplateRetriever(GEN_TWO, TemplateRetriever())

        httpretty.register_uri('GET', TEMPLATES_YML, body=self.mock_get_templates_from_github())

        # Act
        templates = template_retriever.get_templates()

        # Assert
        self.assertEqual(len(templates), 2)
        self.assertEqual(templates['gen2/switch'][0].name, 'gen2/switch')
        self.assertEqual(templates['gen2/switch'][0].description, 'Basic switch template')
        self.assertEqual(templates['gen2/switch'][0].repository, 'https://github.com/QualiSystems/shellfoundry-switch-template')

        self.assertEqual(templates['gen2/software-asset'][0].name, 'gen2/software-asset')
        self.assertEqual(templates['gen2/software-asset'][0].description, 'Basic software-asset template')
        self.assertEqual(templates['gen2/software-asset'][0].repository, 'https://github.com/QualiSystems/shellfoundry-software-asset-template')

    @httpretty.activate
    def test_filtered_template_retriever_all_success(self):
        # Arrange
        template_retriever = FilteredTemplateRetriever(NO_FILTER, TemplateRetriever())

        httpretty.register_uri('GET', TEMPLATES_YML, body=self.mock_get_templates_from_github())

        # Act
        templates = template_retriever.get_templates()

        # Assert
        self.assertEqual(len(templates), 4)
        self.assertEqual(templates['gen1/router'][0].name, 'gen1/router')
        self.assertEqual(templates['gen1/router'][0].description, 'Basic router template')
        self.assertEqual(templates['gen1/router'][0].repository, 'https://github.com/QualiSystems/shellfoundry-router-template')

        self.assertEqual(templates['gen1/switch'][0].name, 'gen1/switch')
        self.assertEqual(templates['gen1/switch'][0].description, 'Basic switch template')
        self.assertEqual(templates['gen1/switch'][0].repository, 'https://github.com/QualiSystems/shellfoundry-switch-template')

        self.assertEqual(templates['gen2/switch'][0].name, 'gen2/switch')
        self.assertEqual(templates['gen2/switch'][0].description, 'Basic switch template')
        self.assertEqual(templates['gen2/switch'][0].repository, 'https://github.com/QualiSystems/shellfoundry-switch-template')

        self.assertEqual(templates['gen2/software-asset'][0].name, 'gen2/software-asset')
        self.assertEqual(templates['gen2/software-asset'][0].description, 'Basic software-asset template')
        self.assertEqual(templates['gen2/software-asset'][0].repository, 'https://github.com/QualiSystems/shellfoundry-software-asset-template')


class TestTemplateRetrieverFakeFS(pyfakefs.fake_filesystem_unittest.TestCase):
    def setUp(self):
        self.setUpPyfakefs()

    def test_get_templates_from_data_folder(self):
        # Arrange
        self.fs.CreateFile('/data/templates.yml', contents="""
templates:
    - name : gen1/resource
      description : 1st generation shell template for basic inventory resources
      repository : https://github.com/QualiSystems/shell-resource-standard
      params:
        project_name :
      min_cs_ver: 7.0
    - name : gen2/software-asset
      params:
        project_name :
        family_name :
      description : 2nd generation shell template for software assets
      repository : https://github.com/QualiSystems/shellfoundry-tosca-software_asset-template
      min_cs_ver: 8.1
""")

        template_retriever = TemplateRetriever()

        # Act
        templates = template_retriever.get_templates(alternative='/data/templates.yml')

        # Assert
        self.assertEqual(len(templates), 2)
        self.assertTrue('gen1/resource' in templates)
        self.assertTrue('gen2/software-asset' in templates)
        self.assertEqual(templates['gen1/resource'][0].standard, None)
        self.assertEqual(templates['gen2/software-asset'][0].standard, 'software-asset')
