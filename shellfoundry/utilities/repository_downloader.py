import os
import zipfile
import requests
from giturlparse import parse

from abc import ABCMeta
from abc import abstractmethod

from shellfoundry.utilities.template_versions import TemplateVersions
from shellfoundry.exceptions import VersionRequestException


class DownloadedRepoExtractor:
    def __init__(self):
        pass

    __metaclass__ = ABCMeta

    @abstractmethod
    def extract_to_folder(self, repo_link, folder):
        pass


class ZipDownloadedRepoExtractor (DownloadedRepoExtractor):

    def extract_to_folder(self, repo_link, folder):
        with zipfile.ZipFile(repo_link, "r") as z:
            infos = z.infolist()
            z.extractall(folder)
        return [info.filename for info in infos]


class RepositoryDownloader:
    def __init__(self, repo_extractor=ZipDownloadedRepoExtractor()):
        self.repo_extractor = repo_extractor

    def download_template(self, target_dir, repo_address, branch=None):
        user, repo = self._parse_repo_url(repo_address)
        if not branch:
            branch = self._get_latest_branch((user, repo))
        download_url = self._join_url_all("https://api.github.com/repos", [user, repo, 'zipball', branch])
        archive_path = ''
        try:
            archive_path = self._download_file(download_url, target_dir)

            repo_content = self.repo_extractor.extract_to_folder(archive_path, target_dir)

            # The first entry is always the root folder by git zipball convention
            root_dir = repo_content[0]

            return os.path.join(target_dir, root_dir)

        finally:
            if os.path.exists(archive_path):
                os.remove(archive_path)

    def _join_url_all(self, url, fragments):
        for frag in fragments:
            url = url + '/' + frag
        return url

    def _try_parse_git_url(self, url):
        if url.startswith('git@'):
            parsed_repo = parse(url)
            return True, parsed_repo.owner, parsed_repo.repo
        else:
            return False, None, None

    def _try_parse_http_url(self, url):
        if url.startswith('http'):
            fragments = url.split("/")
            return True, fragments[-2], fragments[-1]
        else:
            return False, None, None

    def _parse_repo_url(self, url):
        success, user, repo = self._try_parse_git_url(url)
        if not success:
            success, user, repo = self._try_parse_http_url(url)

        return user, repo

    def _download_file(self, url, directory):
        local_filename = os.path.join(directory, url.split('/')[-1])
        # NOTE the stream=True parameter
        r = requests.get(url, stream=True)
        if r.status_code != requests.codes.ok:
            raise VersionRequestException('Failed to download zip file from {}'.format(url))
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:  # filter out keep-alive new chunks
                    f.write(chunk)
                    # f.flush() commented by recommendation from J.F.Sebastian
        return local_filename

    def _get_latest_branch(self, repo):
        return next(iter(TemplateVersions(*repo).get_versions_of_template()))
