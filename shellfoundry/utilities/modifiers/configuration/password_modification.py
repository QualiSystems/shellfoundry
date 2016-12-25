import base64

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
        return node() # returns machine name

    def _decode_encode(self, value, key):
        return ''.join(chr(ord(source) ^ ord(key)) for source, key in zip(value, key * 100))
