from __future__ import annotations

import base64
import binascii
from typing import ClassVar

import shellfoundry.exceptions as exceptions


class PasswordModification:
    HANDLING_KEYS: ClassVar[list[str]] = ["password", "github_password"]

    def modify(self, value: str) -> str:
        encryption_key = self._get_encryption_key()
        encoded = self._decode_encode(value, encryption_key)
        return base64.b64encode(encoded.encode()).decode()

    def normalize(self, value: str) -> str:
        try:
            encryption_key = self._get_encryption_key()
            return self._decode_encode(
                base64.decodebytes(value.encode()).decode(), encryption_key
            )
        except binascii.Error:
            return value

    @staticmethod
    def _get_encryption_key() -> str:
        from platform import node

        machine_name = node()
        if not machine_name:
            raise exceptions.PlatformNameIsEmptyException()
        return machine_name

    @staticmethod
    def _decode_encode(value: str, key: str) -> str:
        return "".join(
            chr(ord(source) ^ ord(key)) for source, key in zip(value, key * 100)
        )
