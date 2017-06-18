import click

from functools import update_wrapper
from shellfoundry.utilities import is_index_version_greater_than_current


def shellfoundry_version_check(f):
    def decorator(*args, **kwargs):
        f(**kwargs)
        is_greater_version, is_major_release = is_index_version_greater_than_current()
        if not is_greater_version:
            return None
        print ''
        if is_major_release:
            click.secho(
                'This version of shellfoundry is not supported anymore, please upgrade by running: pip install shellfoundry --upgrade',
                fg='yellow')
        else:
            click.secho(
                'There is a new version of shellfoundry available, please upgrade by running: pip install shellfoundry --upgrade',
                fg='yellow')

    return update_wrapper(decorator, f)
