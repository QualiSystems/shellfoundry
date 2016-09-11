import os

from requests import post

from shellfoundry.utilities.shell_package import ShellPackage
from cloudshell.rest.api import PackagingRestApiClient


def generate():
    """
    Creates a deployable Shell which can be distributed to a production environment
    """
    path = os.getcwd()
    shell_package = ShellPackage(path)
    shell_filename = shell_package.get_shell_name() + '.zip'
    shell_filename = 'Nxos.zip'
    package_full_path = os.path.join(path, 'dist', shell_filename)
    package_full_path = "C:\\work\\GitHub\\nxos\\dist\\Nxos.zip"

    client = PackagingRestApiClient(ip='localhost',
                                    username='admin',
                                    port='9000',
                                    domain='global',
                                    password='admin')

    url = 'http://localhost:9000/API/ShellDrivers/Generate'
    response = post(url,
                    files={os.path.basename(shell_filename): open(package_full_path, 'rb')},
                    headers={'Authorization': 'Basic ' + client.token})

    print('writing zip file')
    with open('my_driver.zip', 'wb') as driver_file:
        driver_file.write(response.content)

generate()
