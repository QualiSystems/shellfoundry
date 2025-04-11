from __future__ import annotations

import requests
from attrs import define, field
from packaging.version import Version

import shellfoundry.exceptions as exc

VERSIONS_URL = "https://api.github.com/repos/{}/{}/branches"
NAME_PLACEHOLDER = "name"


def is_version(string: str) -> bool:
    try:
        Version(string)  # Try to parse the string as a version
        return True
    except ValueError:
        return False


@define
class TemplateVersions:
    url_user: str
    url_repo: str
    template_repo: list[str] = field(init=False)

    def __attrs_post_init__(self):
        self.template_repo = [self.url_user, self.url_repo]

    def get_versions_of_template(self) -> list[str]:
        """Get all versions (branches) of a given template.

        Raises HTTPError on request fail,
        NoVersionsHaveBeenFoundException when no versions have been found
        :return: List filled with version names (e.g. 1.0, 1.1, 2.0...)
        """
        response = requests.get(VERSIONS_URL.format(*self.template_repo))
        response.raise_for_status()

        branches = [d[NAME_PLACEHOLDER] for d in response.json()]
        branches.sort(reverse=True, key=lambda x: (is_version(x), x))
        if not self.has_versions(branches):
            raise exc.NoVersionsHaveBeenFoundException(
                "No versions have been found for this template"
            )
        return branches

    @staticmethod
    def has_versions(branches: list[str]) -> bool:
        first_branch = next(iter(branches or []), None)
        return first_branch is not None
