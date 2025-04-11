from __future__ import annotations

import json
import os
import re
from typing import ClassVar

import click
from attrs import define, field
from cloudshell.rest.exceptions import FeatureUnavailable
from packaging.version import parse
from requests.exceptions import SSLError

from shellfoundry.constants import (
    ALTERNATIVE_TEMPLATES_PATH,
    MASTER_BRANCH_NAME,
    TEMPLATE_INFO_FILE,
)
from shellfoundry.exceptions import (
    FatalError,
    StandardVersionException,
    VersionRequestException,
)
from shellfoundry.utilities.config_reader import CloudShellConfigReader, Configuration
from shellfoundry.utilities.cookiecutter_integration import CookiecutterTemplateCompiler
from shellfoundry.utilities.repository_downloader import RepositoryDownloader
from shellfoundry.utilities.standards.standards_retriever import Standards
from shellfoundry.utilities.standards.standards_versions import StandardVersionsFactory
from shellfoundry.utilities.temp_dir_context import TempDirContext
from shellfoundry.utilities.template_retriever import TemplateRetriever
from shellfoundry.utilities.template_versions import TemplateVersions
from shellfoundry.utilities.validations.shell_name_validations import (
    ShellNameValidations,
)


@define
class NewCommandExecutor:
    """Creates shell based on template and standards."""

    template_compiler: CookiecutterTemplateCompiler = field(
        factory=CookiecutterTemplateCompiler
    )
    template_retriever: TemplateRetriever = field(factory=TemplateRetriever)
    repository_downloader: RepositoryDownloader = field(factory=RepositoryDownloader)
    standards: Standards = field(factory=Standards)
    standard_versions: StandardVersionsFactory = field(factory=StandardVersionsFactory)
    shell_name_validations: ShellNameValidations = field(factory=ShellNameValidations)
    cloudshell_config_reader: Configuration = field(
        factory=lambda: Configuration(CloudShellConfigReader()), init=False
    )

    LOCAL_TEMPLATE_URL_PREFIX: ClassVar[str] = "local:"
    REMOTE_TEMPLATE_URL_PREFIX: ClassVar[str] = "url:"
    L1_TEMPLATE: ClassVar[str] = "layer-1-switch"

    def new(
        self,
        name: str,
        template: str,
        version: str | None = None,
        python_version: str = "3",
    ) -> None:
        """Create a new shell based on a template.

        version: The desired version of the shell template to use
        name: The name of the Shell
        template: The name of the template to use
        python_version: Python version
        """
        # Special handling for the case where the user runs 'shellfoundry .'
        # in such a case the '.' character is substituted for the shell name
        # and the content of the current folder is populated
        running_on_same_folder = False
        if name == os.path.curdir:
            name = os.path.split(os.getcwd())[1]
            running_on_same_folder = True

        if not self.shell_name_validations.validate_shell_name(name):
            raise click.BadParameter(
                "Shell name must begin with a letter "
                "and contain only alpha-numeric characters and spaces."
            )

        try:
            standards = self.standards.fetch()
        except StandardVersionException as err:
            raise click.ClickException(f"Cannot retrieve standards list. Error: {err}")

        # Get template using direct url path. Ignore parameter in configuration file
        if self._is_direct_online_template(template):
            self._import_direct_online_template(
                name, running_on_same_folder, template, standards, python_version
            )
        # Get template using direct path. Ignore parameter in configuration file
        elif self._is_direct_local_template(template):
            self._import_local_template(
                name, running_on_same_folder, template, standards, python_version
            )
        # Get template from GitHub repository
        elif self.cloudshell_config_reader.read().online_mode.lower() == "true":
            self._import_online_template(
                name,
                running_on_same_folder,
                template,
                version,
                standards,
                python_version,
            )
        # Get template from location defined in shellfoundry configuration
        else:
            template = self._get_local_template_full_path(template, standards, version)
            self._import_local_template(
                name, running_on_same_folder, template, standards, python_version
            )

        if template == self.L1_TEMPLATE:
            click.secho("WARNING: L1 shells support python 2.7 only!", fg="yellow")

        click.echo(f"Created shell {name} based on template {template}")

    def _import_direct_online_template(
        self,
        name: str,
        running_on_same_folder: bool,
        template: str,
        standards: dict[str, list[str]],
        python_version: str,
    ) -> None:
        """Create shell based on template downloaded by the direct link."""
        template_url = self._remove_prefix(
            template, NewCommandExecutor.REMOTE_TEMPLATE_URL_PREFIX
        )
        with TempDirContext(name) as temp_dir:
            try:
                repo_path = self.repository_downloader.download_template(
                    target_dir=temp_dir,
                    repo_address=template_url,
                    branch=None,
                    is_need_construct=False,
                )
            except VersionRequestException:
                raise click.BadParameter(
                    f"Failed to download template from provided direct link {template_url}"  # noqa: E501
                )

            self._verify_template_standards_compatibility(
                template_path=repo_path, standards=standards
            )

            extra_content = self._get_template_params(repo_path=repo_path)

            self.template_compiler.compile_template(
                shell_name=name,
                template_path=repo_path,
                extra_context=extra_content,
                running_on_same_folder=running_on_same_folder,
                python_version=python_version,
            )

    def _import_online_template(
        self,
        name: str,
        running_on_same_folder: bool,
        template: str,
        version: str,
        standards: dict[str, list[str]],
        python_version: str,
    ) -> None:
        """Create shell based on template downloaded from GitHub by the name."""
        # Create a temp folder for the operation to make sure we delete it after
        with TempDirContext(name) as temp_dir:
            try:
                templates = self.template_retriever.get_templates(standards=standards)
            except (SSLError, FatalError):
                raise click.UsageError(
                    "Cannot retrieve templates list, are you offline?"
                )
            except FeatureUnavailable:
                templates = self.template_retriever.get_templates(
                    alternative=ALTERNATIVE_TEMPLATES_PATH, standards=standards
                )

            templates = {
                template_name: template[0]
                for template_name, template in templates.items()
            }

            if template not in templates:
                raise click.BadParameter(
                    f"Template {template} does not exist. "
                    f"Supported templates are: {self._get_templates_with_comma(templates)}"  # noqa: E501
                )
            template_obj = templates[template]

            if not version and template != self.L1_TEMPLATE:
                version = self._get_template_latest_version(
                    standards, template_obj.standard
                )

            try:
                repo_path = self.repository_downloader.download_template(
                    temp_dir, template_obj.repository, version
                )
            except VersionRequestException:
                branches = TemplateVersions(
                    *template_obj.repository.split("/")[-2:]
                ).get_versions_of_template()
                branches.remove(MASTER_BRANCH_NAME)
                branches_str = ", ".join(branches)
                raise click.BadParameter(
                    f"Requested standard version ('{version}') doesn't match template version."  # noqa: E501
                    f" \nAvailable versions for {template_obj.name}: {branches_str}"
                )

            self._verify_template_standards_compatibility(
                template_path=repo_path, standards=standards
            )

            self.template_compiler.compile_template(
                shell_name=name,
                template_path=repo_path,
                extra_context=template_obj.params,
                running_on_same_folder=running_on_same_folder,
                python_version=python_version,
            )

    def _import_local_template(
        self,
        name: str,
        running_on_same_folder: bool,
        template: str,
        standards: dict[str, list[str]],
        python_version: str,
    ) -> None:
        """Create shell based on direct path to local template."""
        repo_path = self._remove_prefix(
            template, NewCommandExecutor.LOCAL_TEMPLATE_URL_PREFIX
        )

        if not os.path.exists(repo_path) or not os.path.isdir(repo_path):
            raise click.BadParameter(
                f"Could not locate a template folder at: {repo_path}"
            )

        extra_content = self._get_template_params(repo_path=repo_path)

        self._verify_template_standards_compatibility(
            template_path=repo_path, standards=standards
        )

        self.template_compiler.compile_template(
            shell_name=name,
            template_path=repo_path,
            extra_context=extra_content,
            running_on_same_folder=running_on_same_folder,
            python_version=python_version,
        )

    def _get_template_latest_version(
        self, standards_list: list[dict[str, list[str]]], standard: str
    ) -> str:
        """Get the latest template version."""
        try:
            return self.standard_versions.create(standards_list).get_latest_version(
                standard
            )
        except Exception as e:
            click.ClickException(str(e))

    def _get_local_template_full_path(
        self,
        template_name: str,
        standards: dict[str, list[str]],
        version: str | None = None,
    ) -> str:
        """Get full path to local template based on provided template name."""
        templates_location = self.cloudshell_config_reader.read().template_location

        templates = self.template_retriever.get_templates(
            template_location=templates_location, standards=standards
        )

        template_obj = templates.get(template_name, None)
        if template_obj is None:
            raise click.BadParameter(
                f"There is no template with name ({template_name}).\n"
                "Please, run command 'shellfoundry list' "
                "to get all available templates."
            )

        avail_standards = set()
        avail_templates = {}
        for template in template_obj:
            avail_standards.update(standards[template.standard])
            avail_templates.update(template.standard_version)

        if version:
            if version in avail_standards:
                if version in avail_templates:
                    return avail_templates[version]["repo"]
                else:
                    raise click.BadParameter(
                        f"Requested template version ({version}) "
                        f"does not exist at templates location ({templates_location}).\n"  # noqa: E501
                        f"Existing template versions: {', '.join(list(avail_templates.keys()))}"  # noqa: E501
                    )
            else:
                raise click.BadParameter(
                    f"Requested template version ({version}) "
                    f"does not compatible with available Standards on CloudShell Server"
                    f" ({', '.join(avail_standards)})"
                )
        else:
            # try to find max available template version
            try:
                version = str(
                    max(
                        list(
                            map(
                                parse,
                                avail_standards & set(avail_templates.keys()),
                            )
                        )
                    )
                )
            except ValueError:
                raise click.ClickException("There are no compatible templates and ")

            return avail_templates[version]["repo"]

    @staticmethod
    def _get_template_params(repo_path: str) -> dict[str, ...]:
        """Determine template additional parameters."""
        full_path = os.path.join(repo_path, TEMPLATE_INFO_FILE)
        if not os.path.exists(full_path):
            raise click.ClickException(
                f"Wrong template path provided. Provided path: {repo_path}"
            )
        with open(full_path, encoding="utf8") as f:
            templ_data = json.load(f)

        family_name = templ_data.get("family_name")
        if isinstance(family_name, list):
            value = click.prompt(
                f"Please, choose one of the possible family name: {', '.join(family_name)}",  # noqa: E501
                default=family_name[0],
            )
            if value not in family_name:
                raise click.UsageError("Incorrect family name provided.")
            extra_context = {"family_name": value}
        elif family_name:
            extra_context = {"family_name": family_name}
        else:
            extra_context = {}

        return extra_context

    @staticmethod
    def _is_direct_local_template(template: str) -> bool:
        return template.startswith(NewCommandExecutor.LOCAL_TEMPLATE_URL_PREFIX)

    @staticmethod
    def _is_direct_online_template(template: str) -> bool:
        return template.startswith(NewCommandExecutor.REMOTE_TEMPLATE_URL_PREFIX)

    @staticmethod
    def _remove_prefix(string: str, prefix: str) -> str:
        return string.rpartition(prefix)[-1]

    @staticmethod
    def _get_templates_with_comma(templates: dict[str, ...]) -> str:
        return ", ".join(list(templates.keys()))

    @staticmethod
    def _verify_template_standards_compatibility(
        template_path: str, standards: dict[str, list[str]]
    ) -> None:
        """Check is template and available standards on cloudshell are compatible."""
        shell_def_path = os.path.join(
            template_path, "{{cookiecutter.project_slug}}", "shell-definition.yaml"
        )
        if os.path.exists(shell_def_path):
            with open(shell_def_path, encoding="utf8") as stream:
                match = re.search(
                    r"cloudshell_standard:\s*cloudshell_(?P<name>\S+)_standard_(?P<version>\S+)\.\w+$",  # noqa: E501
                    stream.read(),
                    re.MULTILINE,
                )
                if match:
                    name = str(match.groupdict()["name"]).replace("_", "-")
                    version = str(match.groupdict()["version"].replace("_", "."))

                    if name not in standards or version not in standards[name]:
                        raise click.ClickException(
                            "Shell template and available standards are not compatible"
                        )
                else:
                    raise click.ClickException(
                        "Can not determine standard version for provided template"
                    )
