from __future__ import annotations

import os
import shutil
from typing import ClassVar

try:
    from pip import main as pip_main
except Exception:
    from pip._internal import main as pip_main


class PythonDependenciesPackager:
    CS_PYPI_PORT: ClassVar[int] = 8036

    def save_offline_dependencies(
        self,
        requirements_path: str,
        dest_path: str,
        cs_server_address: str | None = None,
    ) -> None:
        if os.path.isdir(dest_path):
            shutil.rmtree(path=dest_path, ignore_errors=True)

        if not os.path.exists(requirements_path):
            return

        proxy = os.environ.get("http_proxy")
        pip_args = ["download"]
        if proxy:
            pip_args.append("--proxy")
            pip_args.append(proxy)

        if cs_server_address:
            pip_args.append(
                "--trusted-host={cs_server_address}".format(
                    cs_server_address=cs_server_address
                )
            )
            pip_args.append(
                "--extra-index-url=http://{cs_server_address}:{cs_pypi_port}".format(
                    cs_server_address=cs_server_address, cs_pypi_port=self.CS_PYPI_PORT
                )
            )

        pip_args.append(
            "--requirement={requirements_path}".format(
                requirements_path=requirements_path
            )
        )
        pip_args.append("--dest={dest_path}".format(dest_path=dest_path))
        pip_main(pip_args)
