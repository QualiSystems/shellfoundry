import ConfigParser
import os
from quali_api_client import QualiAPIClient


class ShellInstaller(object):
    def install(self, package_name):
        config = ConfigParser.ConfigParser()

        config_path = os.path.join(os.getcwd(), 'qpm.ini')
        config.readfp(open(config_path))
        host = config.get('Installation', 'host') or 'localhost'
        port = config.get('Installation', 'port') or '9000'
        username = config.get('Installation', 'username') or 'admin'
        password = config.get('Installation', 'password') or 'admin'
        domain = config.get('Installation', 'domain') or 'Global'

        print 'Installing package {0} into CloudShell at http://{1}:{2}'.format(package_name, host, port)
        server = QualiAPIClient(host, port, username, password, domain)
        server.upload_environment_zip_file(os.path.join(os.getcwd(), package_name + '.zip'))
