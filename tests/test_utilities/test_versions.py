#!/usr/bin/python
import unittest
from unittest.mock import MagicMock, patch

from shellfoundry.utilities import is_index_version_greater_than_current

patch.object = patch.object


class TestVersionsHelpers(unittest.TestCase):
    def test_current_version_greater_than_index(self):
        # Arrange
        return_json = """{
                                "info":{
                                "version":"1.0.0"
                                }}"""
        get_response = Mock()
        get_response.status_code = 200
        get_response.content = return_json

        # Act
        with patch('shellfoundry.utilities.get_installed_version', return_value='1.0.0'), \
             patch('shellfoundry.utilities.requests.get', return_value=get_response):
            is_greater_version, is_major_release = is_index_version_greater_than_current()

        # Assert
        self.assertFalse(is_greater_version)
        self.assertFalse(is_major_release)

    def test_current_version_lower_than_index_by_a_patch(self):
        # Arrange
        return_json = """{
                "info":{
                "version":"0.2.8"
                }}"""
        get_response = Mock()
        get_response.status_code = 200
        get_response.content = return_json

        # Act
        with patch('shellfoundry.utilities.get_installed_version', return_value='0.2.7'), \
             patch('shellfoundry.utilities.requests.get', return_value=get_response):
            is_greater_version, is_major_release = is_index_version_greater_than_current()

        # Assert
        self.assertTrue(is_greater_version)
        self.assertFalse(is_major_release)

    def test_current_version_lower_than_index_by_a_major(self):
        # Arrange
        return_json = """{
                        "info":{
                        "version":"1.0.0"
                        }}"""
        get_response = Mock()
        get_response.status_code = 200
        get_response.content = return_json

        # Act
        with patch('shellfoundry.utilities.get_installed_version', return_value='0.2.7'), \
             patch('shellfoundry.utilities.requests.get', return_value=get_response):
            is_greater_version, is_major_release = is_index_version_greater_than_current()

        # Assert
        self.assertTrue(is_greater_version)
        self.assertTrue(is_major_release)

    def test_current_version_is_equal_to_index_version(self):
        # Arrange
        return_json = """{
                        "info":{
                        "version":"0.2.7"
                        }}"""
        get_response = Mock()
        get_response.status_code = 200
        get_response.content = return_json

        # Act
        with patch('shellfoundry.utilities.get_installed_version', return_value='0.2.7'), \
             patch('shellfoundry.utilities.requests.get', return_value=get_response):
            is_greater_version, is_major_release = is_index_version_greater_than_current()

        # Assert
        self.assertFalse(is_greater_version)
        self.assertFalse(is_major_release)
