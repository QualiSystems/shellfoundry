import os


class ShellPackage(object):
    def __init__(self, path):
        self.path = path

    def get_shell_name(self):
        """
        Returns shell name
        :return:
        """
        head, shell_name = os.path.split(self.path)
        return shell_name.title().replace('-', '')

    def is_tosca(self):
        """
        Determines whether a shell is a TOSCA based shell
        :return:
        :rtype: bool
        """
        return os.path.exists(self.get_metadata_path())

    def get_metadata_path(self):
        """
        Returns file path of the TOSCA meta file
        :param path:
        :return: TOSCA.met path
        :rtype: str
        """
        return os.path.join(self.path, 'TOSCA-Metadata', 'TOSCA.meta')
