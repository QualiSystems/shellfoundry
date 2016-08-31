import os


class ShellPackageHelper(object):
    @staticmethod
    def get_shell_name(path):
        """
        Returns shell name
        :param path:
        :return:
        """
        head, shell_name = os.path.split(path)
        return shell_name.title().replace('-', '')

    @staticmethod
    def is_tosca_based_shell(path):
        """
        Determines whether a shell is a TOSCA based shell
        :param path: Path to shell
        :return:
        :rtype: bool
        """
        return os.path.exists(ShellPackageHelper.get_tosca_meta_path(path))

    @staticmethod
    def get_tosca_meta_path(path):
        """
        Returns file path of the TOSCA meta file
        :param path:
        :return: TOSCA.met path
        :rtype: str
        """
        return os.path.join(path, 'TOSCA-Metadata', 'TOSCA.meta')
