from ..cloudshell_api import CloudShellClient


class Standards(object):
    def __init__(self):
        self.cloudshell = CloudShellClient()

    def fetch(self, **kwargs):
        alternative = kwargs.get('alternative', None)
        if not alternative:
            return self._fetch_from_cloudshell()
        return self._fetch_from_alternative_path(alternative)

    def _fetch_from_cloudshell(self):
        cs_client = self.cloudshell.create_client()
        try:
            return cs_client.get_installed_standards()
        except:
            raise

    @staticmethod
    def _fetch_from_alternative_path(alternative_path):
        with open(alternative_path, mode='r') as stream:
            response = stream.read()
        return response
