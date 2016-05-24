DEFAULT_HOST = 'localhost'
DEFAULT_PORT = 9000
DEFAULT_USERNAME = 'admin'
DEFAULT_PASSWORD = 'admin'
DEFAULT_DOMAIN = 'Global'


class InstallConfig(object):
    def __init__(self, host, port, username, password, domain):
        self.domain = domain
        self.password = password
        self.username = username
        self.port = port
        self.host = host

    def __eq__(self, other):
        """
        :param other: An instance of InstallConfig to compare
        :type other InstallConfig
        :return: True of same value, False otherwise
        :rtype bool
        """
        return self.domain == other.domain \
               and self.host == other.host \
                and self.password == other.password \
                and self.port == other.port \
                and self.username == other.username

    @staticmethod
    def get_default():
        return InstallConfig(DEFAULT_HOST, DEFAULT_PORT, DEFAULT_USERNAME, DEFAULT_PASSWORD, DEFAULT_DOMAIN)

