import base64
import shellfoundry.exceptions as exceptions


class PasswordModification(object):
    HANDLING_KEY = 'password'

    def modify(self, value):
        encryption_key = self._get_encryption_key()
        encoded = self._decode_encode(value, encryption_key)
        return base64.b64encode(encoded)

    def normalize(self, value):
        import binascii
        try:
            encryption_key = self._get_encryption_key()
            decoded = self._decode_encode(base64.decodestring(value), encryption_key)
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
        return ''.join(chr(ord(source) ^ ord(key)) for source, key in zip(value, key * 100))
