#!/usr/bin/python
# -*- coding: utf-8 -*-

from shellfoundry.utilities.modifiers.configuration.password_modification import PasswordModification

DEFAULT_HOST = "localhost"
DEFAULT_PORT = 9000
DEFAULT_USERNAME = "admin"
DEFAULT_PASSWORD = "admin"
DEFAULT_DOMAIN = "Global"
DEFAULT_AUTHOR = "Anonymous"


class InstallConfig(object):
    def __init__(self, host, port, username, password, domain, author):
        self.domain = domain
        self.password = self._decode_password(password)
        self.username = username
        self.port = port
        self.host = host
        self.author = author

    def __eq__(self, other):
        """
        :param other: An instance of InstallConfig to compare
        :type other InstallConfig
        :return: True of same value, False otherwise
        :rtype bool
        """
        return self.domain == other.domain \
               and self.host == other.host \
               and self.password == other.password \
               and self.port == other.port \
               and self.username == other.username \
               and self.author == other.author

    @staticmethod
    def get_default():
        return InstallConfig(DEFAULT_HOST, DEFAULT_PORT, DEFAULT_USERNAME, DEFAULT_PASSWORD, DEFAULT_DOMAIN,
                             DEFAULT_AUTHOR)

    def _decode_password(self, password):
        pass_mod = PasswordModification()
        return pass_mod.normalize(password)
