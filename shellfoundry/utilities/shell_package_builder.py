#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import shutil
from io import open

import click
import yaml

from shellfoundry.utilities.archive_creator import ArchiveCreator
from shellfoundry.utilities.shell_package import ShellPackage
from shellfoundry.utilities.temp_dir_context import TempDirContext


class ShellPackageBuilder(object):
    DRIVER_DIR = "src"
    DEPLOY_DIR = "deployments"

    def pack(self, path):
        """Creates TOSCA based Shell package."""
        self._remove_all_pyc(path)
        shell_package = ShellPackage(path)
        shell_name = shell_package.get_shell_name()
        shell_real_name = shell_package.get_name_from_definition()
        with TempDirContext(shell_name) as package_path:
            self._copy_tosca_meta(package_path, "")
            tosca_meta = self._read_tosca_meta(path)

            shell_definition_path = tosca_meta["Entry-Definitions"]

            self._copy_shell_definition(package_path, "", shell_definition_path)

            with open(shell_definition_path, encoding="utf8") as shell_definition_file:
                shell_definition = yaml.safe_load(shell_definition_file)

                if "template_icon" in shell_definition["metadata"]:
                    self._copy_artifact(
                        shell_definition["metadata"]["template_icon"], package_path
                    )

                for node_type in list(shell_definition["node_types"].values()):
                    if "artifacts" not in node_type:
                        continue

                    artifact_path_list = []
                    for artifact_name, artifact in node_type["artifacts"].items():
                        if artifact_name == "driver":
                            artifact_path_list.append(
                                self._create_driver(
                                    path="",
                                    package_path=os.curdir,
                                    dir_path=self.DRIVER_DIR,
                                    driver_name=os.path.basename(artifact["file"]),
                                )
                            )
                        elif artifact_name == "deployment":
                            artifact_path_list.append(
                                self._create_driver(
                                    path="",
                                    package_path=os.curdir,
                                    dir_path=self.DEPLOY_DIR,
                                    driver_name=os.path.basename(artifact["file"]),
                                    mandatory=False,
                                )
                            )

                        self._copy_artifact(artifact["file"], package_path)

            zip_path = self._zip_package(package_path, "", shell_real_name)

            try:
                self._remove_build_artifacts(artifact_path_list)
            except Exception:
                pass

            click.echo("Shell package was successfully created: " + zip_path)

    def _copy_artifact(self, artifact_path, package_path):
        if os.path.exists(artifact_path):
            click.echo("Adding artifact to shell package: " + artifact_path)
            self._copy_file(src_file_path=artifact_path, dest_dir_path=package_path)
        else:
            click.echo("Missing artifact not added to shell package: " + artifact_path)

    def _read_tosca_meta(self, path):
        tosca_meta = {}
        shell_package = ShellPackage(path)
        with open(shell_package.get_metadata_path(), encoding="utf8") as meta_file:
            for meta_line in meta_file:
                (key, val) = meta_line.split(":")
                tosca_meta[key] = val.strip()
        return tosca_meta

    def _copy_shell_icon(self, package_path, path):
        self._copy_file(
            src_file_path=os.path.join(path, "shell-icon.png"),
            dest_dir_path=package_path,
        )

    def _copy_shell_definition(self, package_path, path, shell_definition):
        self._copy_file(
            src_file_path=os.path.join(path, shell_definition),
            dest_dir_path=package_path,
        )

    def _copy_tosca_meta(self, package_path, path):
        shell_package = ShellPackage(path)
        self._copy_file(
            src_file_path=shell_package.get_metadata_path(),
            dest_dir_path=os.path.join(package_path, "TOSCA-Metadata"),
        )

    @staticmethod
    def _remove_all_pyc(package_path):
        for root, dirs, files in os.walk(package_path):
            for file in files:
                if file.endswith(".pyc"):
                    os.remove(os.path.join(root, file))

    @staticmethod
    def _create_driver(path, package_path, dir_path, driver_name, mandatory=True):
        dir_to_zip = os.path.join(path, dir_path)
        if os.path.exists(dir_to_zip):
            zip_file_path = os.path.join(package_path, driver_name)
            ArchiveCreator.make_archive(zip_file_path, "zip", dir_to_zip)
            return os.path.abspath(zip_file_path)
        elif mandatory:
            raise click.ClickException(
                "Invalid driver structure. Can't find '{}' driver folder.".format(
                    dir_path
                )
            )

    @staticmethod
    def _copy_file(src_file_path, dest_dir_path):
        if not os.path.exists(dest_dir_path):
            os.makedirs(dest_dir_path)
        shutil.copy(src_file_path, dest_dir_path)

    @staticmethod
    def _zip_package(package_path, path, package_name):
        zip_file_path = os.path.join(path, "dist", package_name)
        return ArchiveCreator.make_archive(zip_file_path, "zip", package_path)

    @staticmethod
    def _remove_build_artifacts(artifacts_path_list):
        for artifact_path in artifacts_path_list:
            if artifact_path and os.path.exists(artifact_path):
                os.remove(artifact_path)
