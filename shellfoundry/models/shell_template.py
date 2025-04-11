from __future__ import annotations

from attrs import define, field


@define
class ShellTemplate:
    name: str
    description: str
    repository: str
    min_cs_ver: str
    standard: str | None = None
    standard_version: dict | None = field(default={})
    params: dict = field(default={})
