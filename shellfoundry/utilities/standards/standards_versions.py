from .consts import STANDARD_NAME_KEY, VERSIONS_KEY


def trim_standard(standard):
    """
    :type standard str
    :return:
    """
    return standard.lower().lstrip('cloudshell').rstrip('standard').strip('_').replace('_', '-')


class StandardVersionsFactory(object):
    def create(self, standards):
        return StandardVersions(standards)


class StandardVersions(object):
    def __init__(self, standards):
        if not standards:
            import os
            from shellfoundry import __file__ as sf_file
            raise Exception('Standards list is empty. Please verify that {} exists'
                            .format(os.path.join(os.path.dirname(sf_file),
                                                 'data', 'standards.json')))
        for standard in standards:
            standard[STANDARD_NAME_KEY] = trim_standard(standard[STANDARD_NAME_KEY])
        self.standards = standards

    def get_latest_version(self, standard):
        for curr_standard in self.standards:
            if standard in curr_standard.values():
                return max(curr_standard[VERSIONS_KEY])
        raise Exception('Failed to find latest version')
