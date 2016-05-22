class ShellFoundryBaseException(Exception):
    def __init__(self, type1, type2=None):
        super(ShellFoundryBaseException, self).__init__(type1, type2)


class ShellYmlMissingException(ShellFoundryBaseException):
    def __init__(self, type1, type2=None):
        super(ShellYmlMissingException, self).__init__(type1, type2)


class WrongShellYmlException(ShellFoundryBaseException):
    def __init__(self, type1, type2=None):
        super(WrongShellYmlException, self).__init__(type1, type2)
