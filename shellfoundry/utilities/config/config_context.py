import yaml

from shellfoundry.utilities.config_reader import INSTALL


class ConfigContext(object):
    def __init__(self, config_file_path, cfg_creation=None):
        self.config_file_path = config_file_path

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
