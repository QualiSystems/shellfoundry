from cloudshell.rest.api import PackagingRestApiClient
from shellfoundry.exceptions import FatalError
from shellfoundry.utilities.config_reader import Configuration, CloudShellConfigReader
from urllib2 import HTTPError


def create_cloudshell_client(retries=1):
    try:
        cs_client = CloudShellClient().create_client(retries=retries)
    except FatalError:
        raise
    return cs_client


class CloudShellClient(object):
    ConnectionFailureMessage = 'Connection to CloudShell Server failed. Please make sure it is up and running properly.'

    def __init__(self, cs_config=None):
        """
        :type cs_config shellfoundry.models.install_config.InstallConfig
        """
        self._cs_config = cs_config or Configuration(CloudShellConfigReader()).read()

    def create_client(self, **kwargs):
        retries = kwargs.get('retries', 1)
        if retries == 0:
            raise FatalError(self.ConnectionFailureMessage)
        try:
            return self._create_client()
        except FatalError as e:
            retry = retries - 1
            if retry == 0:
                raise e
            return self.create_client(retries=retry)

    def _create_client(self):
        try:
            client = PackagingRestApiClient(ip=self._cs_config.host,
                                            username=self._cs_config.username,
                                            port=self._cs_config.port,
                                            domain=self._cs_config.domain,
                                            password=self._cs_config.password)
            return client
        except (HTTPError, Exception) as e:
            if hasattr(e, 'code') and e.code == 401:
                raise FatalError(u'Login to CloudShell failed. Please verify the credentials in the config')
            raise FatalError(self.ConnectionFailureMessage)
