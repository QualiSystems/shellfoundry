from __future__ import annotations

import json
from importlib.metadata import version
from urllib.error import HTTPError, URLError
from urllib.request import urlopen

import requests
from attrs import define
from packaging.version import Version

from shellfoundry.constants import PACKAGE_NAME
from shellfoundry.exceptions import ShellFoundryVersionException


@define
class Index:
    url: str


def get_installed_version(package_name: str) -> Version:
    return Version(version(package_name))


def is_index_version_greater_than_current() -> tuple[bool, bool]:
    installed = get_installed_version(PACKAGE_NAME)
    index = Version(max_version_from_index())

    is_greater_version = index > installed
    is_major_release = is_greater_version and index.major != installed.major

    return is_greater_version, is_major_release


def max_version_from_index() -> str | None:
    try:
        url = f"https://pypi.org/pypi/{PACKAGE_NAME}/json"
        r = requests.get(url)
        if r.status_code != requests.codes.ok:
            raise ShellFoundryVersionException(
                "Cannot retrieve latest shellfoundry version, are you offline?"
            )
        else:
            content = json.loads(r.content)
            max_version = content["info"]["version"]
            return max_version
    except Exception as err:
        raise ShellFoundryVersionException(
            "Cannot retrieve latest shellfoundry version, "
            f"are you offline? Error: {err}"
        )


def latest_released_version() -> str | None:
    url = f"https://pypi.org/pypi/{PACKAGE_NAME}/json"
    try:
        package_info = json.load(urlopen(url))
        return package_info["info"]["version"]
    except (HTTPError, URLError) as err:
        raise ShellFoundryVersionException(
            f"Cannot retrieve latest shellfoundry version,"
            f" are you offline? Error: {err}"
        )
    except Exception as err:
        raise ShellFoundryVersionException(
            f"Unexpected error during shellfoundry version check. Error: {err}."
        )
