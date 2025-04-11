from __future__ import annotations

import click
from attrs import define, field

from shellfoundry.exceptions import FatalError
from shellfoundry.utilities.shell_package_installer import ShellPackageInstaller


@define
class DeleteCommandExecutor:
    shell_package_installer: ShellPackageInstaller = field(
        factory=ShellPackageInstaller
    )

    def delete(self, shell_name: str) -> None:
        try:
            self.shell_package_installer.delete(shell_name=shell_name)
        except FatalError as err:
            msg = err.message if hasattr(err, "message") else err.args[0]
            click.ClickException(msg)

        click.secho("Successfully deleted shell", fg="green")
