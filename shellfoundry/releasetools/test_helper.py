
import yaml

from cloudshell.shell.core.context import (ResourceCommandContext, ResourceContextDetails, ReservationContextDetails,
                                           ConnectivityContext, InitCommandContext)
from cloudshell.api.cloudshell_api import CloudShellAPISession


def create_session_from_cloudshell_config():

    import inspect
    from os import path
    test_name = inspect.stack()[1][1]
    f = path.join(path.dirname(path.dirname(test_name)), 'cloudshell_config.yml')
    with open(f, 'r') as f:
        doc = yaml.load(f)
    username = doc['install']['username']
    password = doc['install']['password']
    domain = doc['install']['domain']
    host = doc['install']['host']

    return CloudShellAPISession(host, username, password, domain)


def create_autoload_context(address, client_install_path, controller, port):

    context = InitCommandContext()

    resource = ResourceContextDetails()
    resource.name = 'testing'
    resource.address = address
    resource.attributes = {'Client Install Path': client_install_path,
                           'Controller Address': controller,
                           'Controller TCP Port': port}
    context.connectivity = ConnectivityContext()
    context.resource = resource
    return context


def create_command_context(server_address, session, env_name,
                           resource_name, client_install_path, controller_address='', controller_port=''):

    context = ResourceCommandContext()

    context.connectivity = ConnectivityContext()
    context.connectivity.server_address = server_address
    context.connectivity.admin_auth_token = session.token_id

    response = session.CreateImmediateTopologyReservation('tgn unittest', 'admin', 60, False, False, 0, env_name,
                                                          [], [], [])

    context.resource = ResourceContextDetails()
    context.resource.name = resource_name
    context.resource.attributes = {'Client Install Path': client_install_path,
                                   'Controller Address': controller_address,
                                   'Controller TCP Port': controller_port}

    context.reservation = ReservationContextDetails()
    context.reservation.reservation_id = response.Reservation.Id
    context.reservation.owner_user = response.Reservation.Owner
    context.reservation.domain = response.Reservation.DomainName

    return context
