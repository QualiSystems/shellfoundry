#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import unittest

import requests

if sys.version_info >= (3, 0):
    from unittest.mock import MagicMock, patch
else:
    from mock import patch, MagicMock

from shellfoundry.exceptions import NoVersionsHaveBeenFoundException
from shellfoundry.utilities.template_versions import TemplateVersions


def mock_get_branches_from_github(is_empty_response=False):
    if is_empty_response:
        response_content = "[]"
    else:
        response_content = """[
      {
        "name": "5.0.0",
        "commit": {
          "sha": "efe253280a3346c2be23b1a9af4113f2b989f26c",
          "url": "https://api.github.com/repos/user/repo/commits/efe253280a3346c2be23b1a9af4113f2b989f26c"
        }
      },
      {
        "name": "5.0.1",
        "commit": {
          "sha": "e67ec4de2f00fabfe7be35fe412ec400847ccc7d",
          "url": "https://api.github.com/repos/user/repo/commits/e67ec4de2f00fabfe7be35fe412ec400847ccc7d"
        }
      },
      {
        "name": "5.0.2",
        "commit": {
          "sha": "421c20b231b11672411f39f813c93d0f82723f3a",
          "url": "https://api.github.com/repos/user/repo/commits/421c20b231b11672411f39f813c93d0f82723f3a"
        }
      },
      {
        "name": "master",
        "commit": {
          "sha": "b8687aef6a15a4fd9c6daa6b7549470e9e3c4c11",
          "url": "https://api.github.com/repos/user/repo/commits/b8687aef6a15a4fd9c6daa6b7549470e9e3c4c11"
        }
      }
    ]
    """  # noqa E501
    response = requests.models.Response()
    response.status_code = 200
    response._content = str.encode(response_content)
    return response


class TestTemplateVersions(unittest.TestCase):
    def setUp(self):
        self.template_version = TemplateVersions("user", "repo")

    @patch(
        "shellfoundry.utilities.template_versions.requests.get",
        MagicMock(side_effect=requests.HTTPError("Failed to receive versions")),
    )
    def test_get_versions_of_template_error_due_to_request_failed(self):
        with self.assertRaises(requests.HTTPError) as context:
            self.template_version.get_versions_of_template()

        # Assert
        self.assertEqual(str(context.exception), "Failed to receive versions")

    @patch(
        "shellfoundry.utilities.template_versions.requests.get",
        MagicMock(return_value=mock_get_branches_from_github(is_empty_response=True)),
    )
    def test_get_versions_of_template_and_has_no_versions_failure(self):
        with self.assertRaises(NoVersionsHaveBeenFoundException) as context:
            self.template_version.get_versions_of_template()

            # Assert
            self.assertEqual(
                str(context.exception), "No versions have been found for this template"
            )

    @patch(
        "shellfoundry.utilities.template_versions.requests.get",
        MagicMock(return_value=mock_get_branches_from_github()),
    )
    def test_get_versions_of_template_reversed_success(self):
        # Act
        versions = self.template_version.get_versions_of_template()

        # Assert
        self.assertSequenceEqual(versions, ["5.0.2", "5.0.1", "5.0.0", "master"])
