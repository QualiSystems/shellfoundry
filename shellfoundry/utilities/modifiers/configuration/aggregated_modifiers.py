from .password_modification import PasswordModification

DEFAULT_MODIFIER = (lambda x: x)  # Default modifier returns the passed value unchanged


class AggregatedModifiers(object):
    def __init__(self, modifiers=None, default=None):
        self.modifiers = modifiers or {
            PasswordModification.HANDLING_KEY: PasswordModification().modify
        }
        self.default_modifier = default or AggregatedModifiers._default_modifier

    def modify(self, key, value):
        if key in self.modifiers:
            return self.modifiers[key](value)
        return self.default_modifier(value)

    @staticmethod
    def _default_modifier(value):  # Default modifier returns the passed value unchanged
        return value
