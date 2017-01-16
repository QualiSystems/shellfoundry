class ShellTemplate(object):

    def __init__(self, name, description, repository, min_cs_ver, params={}):
        self.name = name
        self.description = description
        self.repository = repository
        self.min_cs_ver = min_cs_ver
        self.params = params
