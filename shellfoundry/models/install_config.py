from __future__ import annotations

from attrs import define, field

from shellfoundry.utilities.modifiers.configuration.password_modification import (
    PasswordModification,
)

DEFAULT_HOST = "localhost"
DEFAULT_PORT = 9000
DEFAULT_USERNAME = "admin"
DEFAULT_PASSWORD = "admin"
DEFAULT_DOMAIN = "Global"
DEFAULT_AUTHOR = "Anonymous"
DEFAULT_ONLINE_MODE = "True"
DEFAULT_TEMPLATE_LOCATION = "Empty"
DEFAULT_GITHUB_LOGIN = ""
DEFAULT_GITHUB_PASSWORD = "gh_pass"


@define
class InstallConfig:
    host: str
    port: int
    username: str
    password: str = field(repr=False)  # Hide password
    domain: str
    author: str
    online_mode: str
    template_location: str | None = None
    github_login: str | None = None
    github_password: str | None = field(default=None, repr=False)

    def __attrs_post_init__(self):
        self.password = self._decode_password(self.password)
        if self.github_password:
            self.github_password = self._decode_password(self.github_password)

    @staticmethod
    def _decode_password(password: str) -> str:
        pass_mod = PasswordModification()
        return pass_mod.normalize(password)

    @classmethod
    def get_default(cls):
        return InstallConfig(
            DEFAULT_HOST,
            DEFAULT_PORT,
            DEFAULT_USERNAME,
            DEFAULT_PASSWORD,
            DEFAULT_DOMAIN,
            DEFAULT_AUTHOR,
            DEFAULT_ONLINE_MODE,
            DEFAULT_TEMPLATE_LOCATION,
            DEFAULT_GITHUB_LOGIN,
            DEFAULT_GITHUB_PASSWORD,
        )
