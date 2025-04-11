from __future__ import annotations

import datetime
import os

from attrs import define, field
from click import ClickException
from cookiecutter.exceptions import OutputDirExistsException
from cookiecutter.main import cookiecutter

from shellfoundry.constants import TEMPLATE_INFO_FILE
from shellfoundry.utilities.config_reader import CloudShellConfigReader, Configuration


@define
class CookiecutterTemplateCompiler:
    """Create Shell structure base on provided template."""

    cloudshell_config_reader: Configuration = field(
        factory=lambda: Configuration(CloudShellConfigReader())
    )

    def compile_template(
        self,
        shell_name: str,
        template_path: str,
        extra_context: dict[str, str],
        running_on_same_folder: bool,
        python_version: str | None = None,
    ) -> None:

        if python_version is None:
            python_version = ""
        else:
            python_version = f' PythonVersion="{python_version}"'

        extra_context.update(
            {
                "project_name": shell_name,
                "full_name": self.cloudshell_config_reader.read().author,
                "release_date": datetime.datetime.now().strftime("%B %Y"),
                "python_version": str(python_version),
            }
        )

        output_dir = os.path.pardir if running_on_same_folder else os.path.curdir

        try:
            cookiecutter(
                template_path,
                no_input=True,
                extra_context=extra_context,
                overwrite_if_exists=False,
                output_dir=output_dir,
            )
        except OutputDirExistsException as err:
            if str(err).startswith("Error: "):
                msg = str(err)[6:].strip()
            else:
                msg = str(err)
            raise ClickException(msg)

    @staticmethod
    def _remove_template_info_file(shell_path: str) -> None:
        """Remove template info file from shell structure."""
        template_info_file_path = os.path.join(shell_path, TEMPLATE_INFO_FILE)
        if os.path.exists(template_info_file_path):
            os.remove(template_info_file_path)
