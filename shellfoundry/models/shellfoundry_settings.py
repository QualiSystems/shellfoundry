from __future__ import annotations

from attrs import define

DEFAULT_DEFAULT_VIEW = "gen2"


@define
class ShellFoundrySettings:
    defaultview: str

    @classmethod
    def get_default(cls):
        return ShellFoundrySettings(DEFAULT_DEFAULT_VIEW)
