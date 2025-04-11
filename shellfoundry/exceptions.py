from __future__ import annotations

import click
from attrs import define


class ShellFoundryBaseException(Exception):
    """Base Shellfoundry exception."""


class ShellYmlMissingException(ShellFoundryBaseException):
    """Configuration file shell.yml missing exception."""


class WrongShellYmlException(ShellFoundryBaseException):
    """Incorrect configuration shell.yml structure exception."""


class NoVersionsHaveBeenFoundException(ShellFoundryBaseException):
    """No template versions have been found exception."""


class VersionRequestException(ShellFoundryBaseException):
    """Exception during shell templates operations."""


@define
class PlatformNameIsEmptyException(ShellFoundryBaseException):
    """Empty platform name exception."""

    message: str = "Machine name is empty"


class FatalError(click.ClickException):
    """Fatal error exception."""

    def show(self, file=None):
        click.secho(f"Error: {self.format_message()}", err=True, fg="red")


class YmlFieldMissingException(Exception):
    """Missing field in YAML-file exception."""


class ShellFoundryVersionException(ShellFoundryBaseException):
    """Getting shellfoundry version exception."""


class StandardVersionException(ShellFoundryBaseException):
    """Exception during operations with standards."""
