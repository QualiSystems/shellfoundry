#!/usr/bin/python
# -*- coding: utf-8 -*-

from .password_modification import PasswordModification

DEFAULT_MODIFIER = (
    lambda x: x
)  # Default modifier returns the passed value unchanged  # noqa: E731


class AggregatedModifiers(object):
    def __init__(self, modifiers=None, default=None):
        self.modifiers = modifiers or {
            key: PasswordModification().modify
            for key in PasswordModification.HANDLING_KEYS
        }
        self.default_modifier = default or AggregatedModifiers._default_modifier

    def modify(self, key, value):
        if key in self.modifiers:
            return self.modifiers[key](value)
        return self.default_modifier(value)

    @staticmethod
    def _default_modifier(value):  # Default modifier returns the passed value unchanged
        return value
