#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import yaml

LAYER_ONE_PREFIX = "CloudshellL1"


class ShellPackage(object):
    def __init__(self, path):
        self.path = path
        self.real_shell_name = None

    def get_shell_name(self):
        """
        Returns shell name
        :return:
        """
        head, shell_name = os.path.split(self.path)
        return shell_name.title().replace('-', '').replace('_', '')

    def get_name_from_definition(self, should_reload=False):
        """
        :param bool should_reload: Should reload from
        :return: template name section from shell-definition.yml or equivalent written in entry definition in tosca.meta
        :rtype: str
        """
        # reload the shell name if persisted member is empty or explicit request for reload
        if not self.real_shell_name or should_reload:
            self._reload_name()
        return self.real_shell_name

    def is_layer_one(self):
        """
        Determines whether a shell is Layer 1
        :return:
        :rtype: bool
        """

        return bool(LAYER_ONE_PREFIX in self.get_shell_name())

    def is_tosca(self):
        """
        Determines whether a shell is a TOSCA based shell
        :return:
        :rtype: bool
        """
        return os.path.exists(self.get_metadata_path())

    def get_metadata_path(self):
        """
        Returns file path of the TOSCA meta file
        :param path:
        :return: TOSCA.meta path
        :rtype: str
        """
        return os.path.join(self.path, 'TOSCA-Metadata', 'TOSCA.meta')

    def _reload_name(self):
        """
        Reloads the name from the entry definition in the tosca.meta file
        :return:
        """
        # fetch entry definition from tosca.meta file
        with open(self.get_metadata_path()) as stream:
            s = stream.read()
            entry_definition = dict(map(str.strip, line.split(':', 1)) for line in s.splitlines())['Entry-Definitions']

        # fetch template name from entry definition file retrieved earlier
        with open(os.path.join(self.path, entry_definition)) as stream:
            definition = yaml.safe_load(stream)
        self.real_shell_name = definition['metadata']['template_name']
