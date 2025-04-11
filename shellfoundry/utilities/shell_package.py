from __future__ import annotations

import os

import yaml
from attrs import define, field

LAYER_ONE_PREFIX = "CloudshellL1"


@define
class ShellPackage:
    path: str
    real_shell_name: str = field(init=False, default=None)

    def get_shell_name(self) -> str:
        """Returns shell name."""
        head, shell_name = os.path.split(self.path)
        return shell_name.title().replace("-", "").replace("_", "")

    def get_name_from_definition(self, should_reload: bool = False) -> str:
        """Get shell name.

        It can be done from shell-definition.yml
        or equivalent written in entry definition in tosca.meta.
        """  # noqa: E501
        # reload the shell name if persisted member is empty or explicit request for reload  # noqa: E501
        if not self.real_shell_name or should_reload:
            self._reload_name()
        return self.real_shell_name

    def is_layer_one(self) -> bool:
        """Determines whether a shell is Layer 1."""
        return bool(LAYER_ONE_PREFIX in self.get_shell_name())

    def is_tosca(self) -> bool:
        """Determines whether a shell is a TOSCA based shell."""
        return os.path.exists(self.get_metadata_path())

    def get_metadata_path(self) -> str:
        """Returns file path of the TOSCA meta file."""
        return os.path.join(self.path, "TOSCA-Metadata", "TOSCA.meta")

    def _reload_name(self) -> None:
        """Reloads the name from the entry definition in the tosca.meta file."""
        # fetch entry definition from tosca.meta file
        with open(self.get_metadata_path()) as stream:
            s = str(stream.read())
            entry_definition = dict(
                list(map(str.strip, line.split(":", 1)))
                for line in s.splitlines()
                if line.strip()
            )["Entry-Definitions"]

        # fetch template name from entry definition file retrieved earlier
        with open(os.path.join(self.path, entry_definition), encoding="utf8") as stream:
            definition = yaml.safe_load(stream)
        self.real_shell_name = definition["metadata"]["template_name"]
