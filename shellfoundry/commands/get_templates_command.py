from __future__ import annotations

import os
import shutil
from threading import Thread, currentThread

import click
import yaml
from attrs import define, field
from requests.exceptions import SSLError

from shellfoundry.exceptions import VersionRequestException
from shellfoundry.utilities.config_reader import CloudShellConfigReader, Configuration
from shellfoundry.utilities.repository_downloader import RepositoryDownloader
from shellfoundry.utilities.temp_dir_context import TempDirContext
from shellfoundry.utilities.template_retriever import TemplateRetriever


@define
class GetTemplatesCommandExecutor:
    """Download all templates relevant to provided CloudShell Version."""

    cloudshell_config_reader: Configuration = field(
        init=False, factory=lambda: Configuration(CloudShellConfigReader())
    )
    repository_downloader: RepositoryDownloader = field(factory=RepositoryDownloader)
    template_retriever: TemplateRetriever = field(factory=TemplateRetriever)

    def get_templates(self, cs_version: str, output_dir: str | None = None) -> None:
        """Download all templates relevant to provided CloudShell Version.

        cs_version: The desired version of the CloudShell
        output_dir: Output directory to download templates
        """
        shellfoundry_config = self.cloudshell_config_reader.read()
        online_mode = shellfoundry_config.online_mode.lower() == "true"
        if online_mode:
            try:
                response = self.template_retriever._get_templates_from_github()
                config = yaml.safe_load(response)
                repos = {template["repository"] for template in config["templates"]}

                if not output_dir:
                    output_dir = os.path.abspath(os.path.curdir)

                archive_name = f"shellfoundry_templates_{cs_version}"

                archive_path = os.path.join(output_dir, f"{archive_name}.zip")
                if os.path.exists(archive_path):
                    click.confirm(
                        text=f"Templates archive for CloudShell Version {cs_version} "
                        f"already exists in path {archive_path}.\n"
                        f"Do you wish to overwrite it?",
                        abort=True,
                    )
                    os.remove(archive_path)

                with TempDirContext(archive_name) as temp_dir:
                    templates_path = temp_dir
                    threads = []
                    errors = []
                    for i, repo in enumerate(repos):
                        template_thread = Thread(
                            name=str(i),
                            target=self.download_template,
                            args=(
                                repo,
                                cs_version,
                                templates_path,
                                shellfoundry_config.github_login,
                                shellfoundry_config.github_password,
                                errors,
                            ),
                        )
                        threads.append(template_thread)

                    for thread in threads:
                        thread.start()
                    for thread in threads:
                        thread.join()

                    if errors:
                        raise click.ClickException(errors[0])

                    os.chdir(output_dir)
                    shutil.make_archive(archive_name, templates_path)

                click.echo(
                    f"Downloaded templates for CloudShell {cs_version} to {os.path.abspath(archive_path)}"  # noqa: E501
                )
            except SSLError:
                raise click.UsageError(
                    "Could not retrieve the templates list to download. Are you offline?"  # noqa: E501
                )
        else:
            click.echo(
                "Please, move shellfoundry to online mode. See, shellfoundry config command"  # noqa: E501
            )

    def download_template(
        self,
        repository: str,
        cs_version: str,
        templates_path: str,
        github_login: str,
        github_password: str,
        errors: list[str],
    ) -> None:
        """Download template from remote repository."""
        try:
            result_branch = self.template_retriever.get_latest_template(
                repository, cs_version, github_login, github_password
            )

            if result_branch:
                try:
                    template_path = os.path.join(
                        templates_path, currentThread().getName()
                    )
                    os.mkdir(template_path)
                    res = self.repository_downloader.download_template(
                        target_dir=template_path,
                        repo_address=repository,
                        branch=result_branch,
                        is_need_construct=True,
                    )

                    shutil.copytree(
                        res, os.path.join(templates_path, repository.split("/")[-1])
                    )
                    shutil.rmtree(path=template_path, ignore_errors=True)
                except VersionRequestException:
                    errors.append(
                        f"Failed to download template from repository {repository} version {result_branch}"  # noqa: E501
                    )
                except shutil.Error:
                    errors.append(
                        f"Failed to build correct template '{repository}' structure"
                    )
                finally:
                    pass

        except click.ClickException as err:
            errors.append(str(err))
