from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar
from urllib.error import HTTPError

from attrs import define, field
from cloudshell.rest.api import PackagingRestApiClient

from shellfoundry.exceptions import FatalError
from shellfoundry.utilities.config_reader import CloudShellConfigReader, Configuration

if TYPE_CHECKING:
    from shellfoundry.models.install_config import InstallConfig


def create_cloudshell_client(retries: int = 1) -> PackagingRestApiClient:
    return CloudShellClient().create_client(retries=retries)


@define
class CloudShellClient:
    """Creates cloudshell client."""

    cs_config: InstallConfig = field(
        factory=lambda: Configuration(CloudShellConfigReader()).read()
    )
    ConnectionFailureMessage: ClassVar[str] = (
        "Connection to CloudShell Server failed. "
        "Please make sure it is up and running properly."
    )

    def create_client(self, **kwargs) -> PackagingRestApiClient | None:
        retries = kwargs.get("retries", 1)

        while retries > 0:
            try:
                return self._create_client()
            except FatalError as e:
                retries -= 1
                if retries == 0:
                    raise e

    def _create_client(self) -> PackagingRestApiClient:
        try:
            return PackagingRestApiClient.login(
                host=self.cs_config.host,
                port=self.cs_config.port,
                username=self.cs_config.username,
                password=self.cs_config.password,
                domain=self.cs_config.domain,
            )
        except (HTTPError, Exception) as e:
            if hasattr(e, "code") and e.code == 401:
                if hasattr(e, "msg") and e.msg:
                    msg = e.msg
                else:
                    msg = "Please verify the credentials in the config"
                raise FatalError(f"Login to CloudShell failed. {msg}")
            raise FatalError(self.ConnectionFailureMessage)
