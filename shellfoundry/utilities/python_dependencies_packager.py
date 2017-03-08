import pip
import os

import shutil


class PythonDependenciesPackager:

    def __init__(self):
        pass

    def save_offline_dependencies(self, requirements_path, dest_path):

        if os.path.isdir(dest_path):
            shutil.rmtree(path=dest_path, ignore_errors=True)

        if not os.path.exists(requirements_path):
            return

        proxy = os.environ.get('http_proxy')
        pip_args = ['download']
        if proxy:
            pip_args.append('--proxy')
            pip_args.append(proxy)
        pip_args.append('--requirement={requirements_path}'.format(requirements_path=requirements_path))
        pip_args.append('--dest={dest_path}'.format(dest_path=dest_path))
        pip.main(pip_args)
