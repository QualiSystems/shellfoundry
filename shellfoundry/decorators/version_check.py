import click

from functools import update_wrapper
from shellfoundry.utilities import is_index_version_greater_than_current


class shellfoundry_version_check(object):
    def __init__(self, abort_if_major=False):
        self.abort_if_major = abort_if_major

    def __call__(self, f):
        def decorator(*args, **kwargs):
            output = ''
            is_greater_version, is_major_release = is_index_version_greater_than_current()
            if is_greater_version:
                if is_major_release:
                    output = 'This version of shellfoundry is not supported anymore, please upgrade by running: pip install shellfoundry --upgrade'

                    if self.abort_if_major:
                        click.secho(output, fg='yellow')
                        print ''
                        raise click.Abort()
                else:
                    output = 'There is a new version of shellfoundry available, please upgrade by running: pip install shellfoundry --upgrade'

            f(**kwargs)

            if output:
                print ''
                click.secho(output, fg='yellow')

        return update_wrapper(decorator, f)
