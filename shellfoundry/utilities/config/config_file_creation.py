import click


class ConfigFileCreation(object):
    def create(self, config_file_path):
        import os
        if os.path.exists(config_file_path):
            return
        try:
            click.echo('Creating config file...')
            open(config_file_path, mode='w').close()
        except:
            if not os.path.exists(config_file_path):
                click.echo('Failed to create config file')
                import sys
                click.echo(sys.exc_info()[1].message)
                raise
