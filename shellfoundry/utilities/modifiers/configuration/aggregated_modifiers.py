from __future__ import annotations

from typing import Any, Callable

from attrs import define, field

from .password_modification import PasswordModification


@define
class AggregatedModifiers:
    modifiers: dict = field(
        factory=lambda: {
            key: PasswordModification().modify
            for key in PasswordModification.HANDLING_KEYS
        }
    )
    default: Callable[[str], str] | None = None
    default_modifier: Callable[[Any], Any] = field(init=False)

    def __attrs_post_init__(self):
        self.default_modifier = self.default or AggregatedModifiers._default_modifier

    def modify(self, key: str, value: str) -> str:
        return self.modifiers.get(key, self.default_modifier)(value)

    @staticmethod
    def _default_modifier(value: Any) -> Any:
        """Default modifier.

        Default modifier returns the passed value unchanged
        """
        return value
