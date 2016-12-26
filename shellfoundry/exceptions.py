class ShellFoundryBaseException(Exception):
    def __init__(self, message):
        super(ShellFoundryBaseException, self).__init__(message)


class ShellYmlMissingException(ShellFoundryBaseException):
    def __init__(self, message):
        super(ShellYmlMissingException, self).__init__(message)


class WrongShellYmlException(ShellFoundryBaseException):
    def __init__(self, message):
        super(WrongShellYmlException, self).__init__(message)


class NoVersionsHaveBeenFoundException(ShellFoundryBaseException):
    def __init__(self, message):
        super(NoVersionsHaveBeenFoundException, self).__init__(message)

class VersionRequestException(ShellFoundryBaseException):
    def __init__(self, message):
        super(VersionRequestException, self).__init__(message)

class PlatformNameIsEmptyException(ShellFoundryBaseException):
    def __init__(self, message='Machine name is empty'):
        super(PlatformNameIsEmptyException, self).__init__(message)

