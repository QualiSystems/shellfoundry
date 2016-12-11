DEFAULT_DEFAULT_VIEW = 'all'

class ShellFoundrySettings(object):
    def __init__(self, defaultview):
        self.defaultview = defaultview

    @staticmethod
    def get_default():
        return ShellFoundrySettings(DEFAULT_DEFAULT_VIEW)

