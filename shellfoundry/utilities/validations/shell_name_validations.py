import re


class ShellNameValidations(object):
    MAX_LENGTH_FOR_NAME = 60
    NAME_REGEX = re.compile("^[a-zA-Z][A-Za-z0-9_ -]*$", re.U)

    def validate_shell_name(self, shell_name):
        match = self.NAME_REGEX.match(shell_name)
        return len(shell_name) < self.MAX_LENGTH_FOR_NAME and match is not None
