#!/usr/bin/python
# -*- coding: utf-8 -*-

import base64
import binascii
import sys

import shellfoundry.exceptions as exceptions


class PasswordModification(object):
    HANDLING_KEYS = ["password", "github_password"]

    def modify(self, value):
        encryption_key = self._get_encryption_key()
        encoded = self._decode_encode(value, encryption_key)
        if sys.version_info[0] < 3:
            return base64.b64encode(encoded)
        else:
            return base64.b64encode(encoded.encode()).decode()

    def normalize(self, value):
        try:
            encryption_key = self._get_encryption_key()
            if sys.version_info[0] < 3:
                decoded = self._decode_encode(
                    base64.decodestring(value), encryption_key
                )
            else:
                decoded = self._decode_encode(
                    base64.decodebytes(value.encode()).decode(), encryption_key
                )
            return decoded
        except binascii.Error:
            return value

    def _get_encryption_key(self):
        from platform import node

        machine_name = node()
        if not machine_name:
            raise exceptions.PlatformNameIsEmptyException()
        return machine_name

    def _decode_encode(self, value, key):
        return "".join(
            chr(ord(source) ^ ord(key)) for source, key in zip(value, key * 100)
        )
