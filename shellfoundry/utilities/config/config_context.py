import yaml
import click

from shellfoundry.utilities.config_reader import INSTALL


class ConfigContext(object):
    def __init__(self, config_file_path):
        self.config_file_path = config_file_path
        self.create_config_file_if_needed(config_file_path)

    @staticmethod
    def create_config_file_if_needed(config_file_path):
        import os
        if os.path.exists(config_file_path):
            return
        # with open(config_file_path, mode='a+') as stream:
        try:
            click.echo('Creating config file...')
            open(config_file_path, mode='w').close()
        except:
            if not os.path.exists(config_file_path):
                click.echo('Failed to create config file')
                import sys
                click.echo(sys.exc_info()[0])
                raise

    def try_save(self, key, value):
        try:
            with open(self.config_file_path, mode='r+') as stream:
                data = yaml.load(stream) or {INSTALL: dict()}
                data[INSTALL][key] = value
                stream.seek(0)
                stream.truncate()
                yaml.safe_dump(data, stream=stream, default_flow_style=False)
            return True
        except:
            return False

    def try_delete(self, key):
        try:
            with open(self.config_file_path, mode='r+') as stream:
                data = yaml.load(stream)
                del data[INSTALL][key] # handle cases that INSTALL does not exists
                stream.seek(0)
                stream.truncate()
                yaml.safe_dump(data, stream=stream, default_flow_style=False)
            return True
        except:
            return False
