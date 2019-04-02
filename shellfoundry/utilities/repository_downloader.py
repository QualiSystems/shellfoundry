#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import zipfile
import requests

from abc import ABCMeta
from abc import abstractmethod

from .template_url import construct_template_url
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
        super(ZipDownloadedRepoExtractor, self).extract_to_folder(repo_link, folder)
        with zipfile.ZipFile(repo_link, "r") as z:
            infos = z.infolist()
            z.extractall(folder)
        return [info.filename for info in infos]


class RepositoryDownloader(object):
    def __init__(self, repo_extractor=ZipDownloadedRepoExtractor()):
        self.repo_extractor = repo_extractor

    def download_template(self, target_dir, repo_address, branch, is_need_construct=True):
        if is_need_construct:
            download_url = construct_template_url(repo_address, branch)
        else:
            download_url = repo_address
        archive_path = ''
        try:
            archive_path = self.download_file(download_url, target_dir)

            repo_content = self.repo_extractor.extract_to_folder(archive_path, target_dir)

            # The first entry is always the root folder by git zipball convention
            root_dir = repo_content[0]

            return os.path.join(target_dir, root_dir)
        finally:
            if os.path.exists(archive_path):
                os.remove(archive_path)

    def download_file(self, url, directory):
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
