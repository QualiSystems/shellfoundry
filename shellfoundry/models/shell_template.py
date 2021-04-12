#!/usr/bin/python
# -*- coding: utf-8 -*-


class ShellTemplate(object):
    def __init__(
        self,
        name,
        description,
        repository,
        min_cs_ver,
        standard=None,
        standard_version=None,
        params=None,
    ):
        self.name = name
        self.description = description
        self.repository = repository
        self.min_cs_ver = min_cs_ver
        self.standard = standard
        self.standard_version = standard_version or {}
        self.params = params or {}
