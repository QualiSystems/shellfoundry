#!/usr/bin/python

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


class InstallConfig(object):
    def __init__(
        self,
        host,
        port,
        username,
        password,
        domain,
        author,
        online_mode,
        template_location,
        github_login,
        github_password,
    ):
        self.domain = domain
        self.password = self._decode_password(password)
        self.username = username
        self.port = port
        self.host = host
        self.author = author
        self.online_mode = online_mode
        self.template_location = template_location
        self.github_login = github_login
        self.github_password = self._decode_password(github_password)

    def __eq__(self, other):
        """Comparison.

        :param other: An instance of InstallConfig to compare
        :type other InstallConfig
        :return: True of same value, False otherwise
        :rtype bool
        """
        return (
            self.domain == other.domain
            and self.host == other.host
            and self.password == other.password
            and self.port == other.port
            and self.username == other.username
            and self.author == other.author
            and self.online_mode == other.online_mode
            and self.template_location == other.template_location
            and self.github_login == other.github_login
            and self.github_password == other.github_password
        )

    @staticmethod
    def get_default():
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

    def _decode_password(self, password):
        pass_mod = PasswordModification()
        return pass_mod.normalize(password)
