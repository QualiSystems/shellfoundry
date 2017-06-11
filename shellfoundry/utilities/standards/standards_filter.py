from collections import OrderedDict


def trim_standard(standard):
    """
    :type standard str
    :return:
    """
    return standard.lower().lstrip('cloudshell').rstrip('standard').strip('_').replace('_', '-')


class StandardsFilter(object):
    def __init__(self):
        pass

    def filter(self, standards, templates):
        """
        :type templates collections.OrderedDict
        :type standards list
        :return:
        """
        ordered = [trim_standard(standard['StandardName']) for standard in standards]
        template_names = [x.name for x in templates.itervalues() if
                          x.standard in ordered]  # creates a list of all matching templates names by available standard

        return OrderedDict((name, templates[name])for name in template_names)


class StandardVersions(object):
    def __init__(self, standards):
        for standard in standards:
            standard['StandardName'] = trim_standard(standard['StandardName'])
        self.standards = standards

    def get_latest_version(self, standard):
        for curr_standard in self.standards:
            if standard in curr_standard.values():
                return max(curr_standard['Versions'])
