from cloudshell.rest.api import PackagingRestApiClient
from shellfoundry.exceptions import FatalError
from shellfoundry.utilities.config_reader import Configuration, CloudShellConfigReader
from urllib2 import HTTPError


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
        except:
            return self.create_client(retries=retries-1)

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
