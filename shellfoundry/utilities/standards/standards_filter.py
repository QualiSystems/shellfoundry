from collections import OrderedDict

class StandardsFilter(object):
    def __init__(self):
        pass

    def filter(self, standards, templates):
        """
        :type templates collections.OrderedDict
        :type standards list
        :return:
        """
        ordered = [self._trim_standard(standard['StandardName']) for standard in standards]
        template_names = [x.name for x in templates.itervalues() if
                          x.standard in ordered]  # creates a list of all matching templates names by available standard

        return OrderedDict((name, templates[name])for name in template_names)

    @staticmethod
    def _trim_standard(standard):
        """
        :type standard str
        :return:
        """
        return standard.lower().lstrip('cloudshell').rstrip('standard').strip('_').replace('_', '-')
