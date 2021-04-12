#!/usr/bin/python
# -*- coding: utf-8 -*-

DEFAULT_DEFAULT_VIEW = "gen2"


class ShellFoundrySettings(object):
    def __init__(self, defaultview):
        self.defaultview = defaultview

    @staticmethod
    def get_default():
        return ShellFoundrySettings(DEFAULT_DEFAULT_VIEW)
