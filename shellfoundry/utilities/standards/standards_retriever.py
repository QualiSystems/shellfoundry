from __future__ import annotations

import json

import click
from cloudshell.rest.exceptions import FeatureUnavailable, PackagingRestApiError

from ..cloudshell_api.client_wrapper import create_cloudshell_client

from shellfoundry.constants import ALTERNATIVE_STANDARDS_PATH
from shellfoundry.exceptions import FatalError, StandardVersionException

STANDARD_NAME_KEY = "StandardName"
VERSIONS_KEY = "Versions"


class Standards:
    def fetch(self) -> dict[str, list[str]]:
        """Get all available standards.

        Try to get standards from Cloudshell.
        In case of error, try to get standards from local built-in file.
        """
        try:
            cs_client = create_cloudshell_client()
            raw_standards = cs_client.get_installed_standards()
        except (FatalError, FeatureUnavailable, PackagingRestApiError) as e:
            click.secho(
                message=f"Can not get standards from Cloudshell Server. Error: {e}",
                fg="yellow",
            )
            try:
                with open(ALTERNATIVE_STANDARDS_PATH, encoding="utf8") as f:
                    raw_standards = json.load(f)
            except Exception:
                raise StandardVersionException(
                    "Error during getting standards either from the server or locally"
                )

        return self._convert_standards(raw_standards=raw_standards)

    @staticmethod
    def _convert_standards(
        raw_standards: list[dict[str, str | list[str]]]
    ) -> dict[str, list[str]]:
        """Convert standards to user-friendly view."""
        return {
            i[STANDARD_NAME_KEY]
            .lower()
            .lstrip("cloudshell")
            .rstrip("standard")
            .strip("_")
            .replace("_", "-"): i[VERSIONS_KEY]
            for i in raw_standards
        }
