from __future__ import annotations

import os

from attrs import define, field
from packaging.version import parse

from shellfoundry import __file__ as sf_file
from shellfoundry.exceptions import StandardVersionException


class StandardVersionsFactory:
    def create(self, standards: dict[str, list[str]]) -> StandardVersions:
        return StandardVersions(standards)


@define
class StandardVersions:
    standards: dict[str, list[str]] = field()

    @standards.validator
    def is_standards_exist(self, attribute, value):
        if not value:
            raise StandardVersionException(
                f"Standards list is empty. "
                f"Please verify that {os.path.join(os.path.dirname(sf_file), 'data', 'standards.json')} exists"  # noqa: E501
            )

    def get_latest_version(self, standard: str) -> str:
        """Get the latest standard version."""
        standards = self.standards.get(standard)
        if not standards:
            raise StandardVersionException("Failed to find latest version")

        return str(max(list(map(parse, standards))))
