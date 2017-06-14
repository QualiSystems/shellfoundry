import unittest

from shellfoundry.utilities.template_url import construct_template_url


class TestTemplateUrl(unittest.TestCase):
    def test_git_url(self):
        # Arrange
        repo_git = 'git@github.com:QualiSystems/shellfoundry.git'

        # Act
        url = construct_template_url(repo_git, 'master')

        # Assert
        self.assertEqual(url, 'https://api.github.com/repos/QualiSystems/shellfoundry/zipball/master')

    def test_http_url(self):
        # Arrange
        repo_git = 'https://github.com/QualiSystems/shellfoundry'

        # Act
        url = construct_template_url(repo_git, 'master')

        # Assert
        self.assertEqual(url, 'https://api.github.com/repos/QualiSystems/shellfoundry/zipball/master')
