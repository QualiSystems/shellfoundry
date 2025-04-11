from __future__ import annotations

import os
import zipfile
from abc import ABC, abstractmethod

import requests
from attrs import define, field

from .template_url import construct_template_url

from shellfoundry.exceptions import VersionRequestException


class DownloadedRepoExtractor(ABC):
    @abstractmethod
    def extract_to_folder(self, repo_link, folder):
        pass


class ZipDownloadedRepoExtractor(DownloadedRepoExtractor):
    def extract_to_folder(self, repo_link: str, folder: str) -> list[str]:
        super().extract_to_folder(repo_link, folder)
        with zipfile.ZipFile(repo_link, "r") as z:
            infos = z.infolist()
            z.extractall(folder)
        return [info.filename for info in infos]


@define
class RepositoryDownloader:
    repo_extractor: DownloadedRepoExtractor = field(factory=ZipDownloadedRepoExtractor)

    def download_template(
        self,
        target_dir: str,
        repo_address: str,
        branch: str,
        is_need_construct: bool = True,
    ) -> str | None:
        if is_need_construct:
            download_url = construct_template_url(repo_address, branch)
        else:
            download_url = repo_address
        archive_path = ""
        try:
            archive_path = self.download_file(download_url, target_dir)

            repo_content = self.repo_extractor.extract_to_folder(
                archive_path, target_dir
            )

            # The first entry is always the root folder by git zipball convention
            root_dir = repo_content[0]

            return os.path.join(target_dir, root_dir)
        finally:
            if os.path.exists(archive_path):
                os.remove(archive_path)

    @staticmethod
    def download_file(url: str, directory: str) -> str:
        local_filename = os.path.join(directory, url.split("/")[-1])
        # NOTE the stream=True parameter
        r = requests.get(url, stream=True)
        if r.status_code != requests.codes.ok:
            raise VersionRequestException(f"Failed to download zip file from {url}")
        with open(local_filename, "wb") as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:  # filter out keep-alive new chunks
                    f.write(chunk)
                    # f.flush() commented by recommendation from J.F.Sebastian
        return local_filename
