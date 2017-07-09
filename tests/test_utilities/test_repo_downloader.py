from unittest import TestCase
import httpretty
from mock import Mock
from pyfakefs import fake_filesystem_unittest
from shellfoundry.utilities.repository_downloader import RepositoryDownloader, DownloadedRepoExtractor
import requests
import os


class TestRepositoryDownloader(fake_filesystem_unittest.TestCase):
    def setUp(self):
        self.setUpPyfakefs()

        from requests.utils import DEFAULT_CA_BUNDLE_PATH
        self.fs.CreateFile(DEFAULT_CA_BUNDLE_PATH)

    @httpretty.activate  # much preferred way than httpretty.enable because it combine enable and disable in one line
    def test_extracts_and_calls_api_url_from_https_addrses(self):
        test_dir = '/test_dir'
        self.fs.CreateDirectory(test_dir)

        input_https_address = "https://api.github.com/org/repo"
        expected_api_url = "https://api.github.com/repos/org/repo/zipball/master"
        expected_versions_url = 'https://api.github.com/repos/org/repo/branches'

        httpretty.register_uri(httpretty.GET, expected_api_url,
                               body="repo-main/,repo-main/shell.txt,repo-main/datamodel/datamodel.xml", streaming=True,
                               status=200)
        httpretty.register_uri(httpretty.GET, expected_versions_url, body="[{\"name\": \"master\"}]", streaming=True,
                               status=200)

        RepositoryDownloader(repo_extractor=TestRepositoryDownloader.FakeExtractor(self.fs)) \
            .download_template(test_dir, input_https_address, 'master')

        self.assertIsNotNone(httpretty.last_request())

    @httpretty.activate  # much preferred way than httpretty.enable because it combine enable and disable in one line
    def test_extracts_and_calls_api_url_from_git_addrses(self):
        test_dir = '/test_dir'
        self.fs.CreateDirectory(test_dir)

        input_https_address = "git@github.com:org/repo.git"
        expected_api_url = "https://api.github.com/repos/org/repo/zipball/master"
        expected_versions_url = 'https://api.github.com/repos/org/repo/branches'

        httpretty.register_uri(httpretty.GET, expected_api_url,
                               body="repo-main/,repo-main/shell.txt,repo-main/datamodel/datamodel.xml", streaming=True,
                               status=200)
        httpretty.register_uri(httpretty.GET, expected_versions_url, body="[{\"name\": \"master\"}]", streaming=True,
                               status=200)

        RepositoryDownloader(repo_extractor=TestRepositoryDownloader.FakeExtractor(self.fs)) \
            .download_template(test_dir, input_https_address, 'master')

        self.assertIsNotNone(httpretty.last_request())

    @httpretty.activate  # much preferred way than httpretty.enable because it combine enable and disable in one line
    def test_returns_the_root_folder_of_the_git_repo(self):
        test_dir = '/test_dir'
        self.fs.CreateDirectory(test_dir)

        input_https_address = "git@github.com:org/repo.git"
        expected_api_url = "https://api.github.com/repos/org/repo/zipball/master"
        expected_versions_url = 'https://api.github.com/repos/org/repo/branches'

        httpretty.register_uri(httpretty.GET, expected_api_url,
                               body="repo-main/,repo-main/shell.txt,repo-main/datamodel/datamodel.xml", streaming=True,
                               status=200)
        httpretty.register_uri(httpretty.GET, expected_versions_url, body="[{\"name\": \"master\"}]", streaming=True,
                               status=200)

        result = RepositoryDownloader(repo_extractor=TestRepositoryDownloader.FakeExtractor(self.fs)) \
            .download_template(test_dir, input_https_address, 'master')

        self.assertEqual(result, os.path.join(test_dir, "repo-main/"))

    class FakeExtractor(DownloadedRepoExtractor):
        def __init__(self, fs):
            super(TestRepositoryDownloader.FakeExtractor, self).__init__()
            self.fs = fs

        def extract_to_folder(self, repo_link, folder):
            files = []
            with open(repo_link, "r") as f:
                content = f.read().replace('\n', '')

            for file in content.split(','):
                if file.endswith('/'):
                    self.fs.CreateDirectory(os.path.join(folder, file))
                else:
                    self.fs.CreateFile(os.path.join(folder, file))
                files.append(file)

            return files
