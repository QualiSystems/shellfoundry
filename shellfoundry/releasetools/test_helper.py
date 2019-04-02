
import time
import yaml

from cloudshell.shell.core.context import (ResourceCommandContext, ResourceContextDetails, ReservationContextDetails,
                                           ConnectivityContext, InitCommandContext)
from cloudshell.api.cloudshell_api import CloudShellAPISession, ResourceAttributesUpdateRequest
from cloudshell.shell.core.session.cloudshell_session import CloudShellSessionContext


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


def create_autoload_context(address, client_install_path='', controller='', port='', user='', password=''):

    session = CloudShellAPISession('localhost', 'admin', 'admin', 'Global')

    context = InitCommandContext()

    resource = ResourceContextDetails()
    resource.name = 'testing'
    resource.address = address
    resource.attributes = {'Client Install Path': client_install_path,
                           'Controller Address': controller,
                           'Controller TCP Port': port,
                           'User': user,
                           'Password': password}
    context.connectivity = ConnectivityContext()
    context.resource = resource
    context.connectivity.server_address = 'localhost'
    context.connectivity.admin_auth_token = session.token_id
    context.connectivity.cloudshell_api_scheme = CloudShellSessionContext.DEFAULT_API_SCHEME
    return context


def create_autoload_context_2g(model, address, controller='', port='', client_install_path='', user='', password=''):

    session = CloudShellAPISession('localhost', 'admin', 'admin', 'Global')

    context = InitCommandContext()

    resource = ResourceContextDetails()
    resource.name = 'testing'
    resource.address = address
    resource.attributes = {model + '.Controller Address': controller,
                           model + '.Controller TCP Port': port,
                           model + '.Client Install Path': client_install_path,
                           model + '.User': user,
                           model + '.Password': password}
    context.connectivity = ConnectivityContext()
    context.connectivity.server_address = 'localhost'
    context.connectivity.admin_auth_token = session.token_id
    context.connectivity.cloudshell_api_scheme = CloudShellSessionContext.DEFAULT_API_SCHEME

    context.resource = resource
    context.resource.family = 'CS_TrafficGeneratorChassis'
    context.resource.model = model
    return context


def create_autoload_resource(session, model, address, name, attributes):
    resource = session.CreateResource(resourceFamily='CS_TrafficGeneratorChassis',
                                      resourceModel=model,
                                      resourceName=name,
                                      resourceAddress=address,
                                      folderFullPath='Testing',
                                      parentResourceFullPath='',
                                      resourceDescription='should be removed after test')
    session.UpdateResourceDriver(resource.Name, model)
    session.SetAttributesValues(ResourceAttributesUpdateRequest(resource.Name, attributes))
    return resource


def create_command_context_old(server_address, session, env_name,
                               resource_name, client_install_path='', controller_address='', controller_port='',
                               user='', password=''):

    context = ResourceCommandContext()
    context.connectivity = ConnectivityContext()
    context.connectivity.server_address = server_address
    context.connectivity.admin_auth_token = session.token_id
    context.connectivity.cloudshell_api_scheme = CloudShellSessionContext.DEFAULT_API_SCHEME

    reservation = session.CreateImmediateTopologyReservation('tgn unittest', 'admin', 60, False, False, 0, env_name,
                                                             [], [], [])
    reservation_id = reservation.Reservation.Id

    context.resource = ResourceContextDetails()
    context.resource.name = resource_name
    context.resource.attributes = {'Client Install Path': client_install_path,
                                   'Controller Address': controller_address,
                                   'Controller TCP Port': controller_port,
                                   'User': user,
                                   'Password': password}

    context.reservation = ReservationContextDetails()
    context.reservation.reservation_id = reservation_id
    context.reservation.owner_user = reservation.Reservation.Owner
    context.reservation.domain = reservation.Reservation.DomainName

    return context


def create_command_context(session, ports, controller, attributes):

    """ Create command context from scratch.

    :param session: CloudShell API session
    :type session: cloudshell.api.cloudshell_api.CloudShellAPISession
    :param controller: TG controller name
    :param ports: list of TG port resources address ['chassis/module/port',...]
    :param attributes: for driver tests - dictionary {name: value} of TG controller attributes
                       for shell tests - list [AttributeNameValue] of TG controller attributes
    """

    context = ResourceCommandContext()
    context.connectivity = ConnectivityContext()
    context.connectivity.server_address = session.host
    context.connectivity.admin_auth_token = session.token_id
    context.connectivity.cloudshell_api_scheme = CloudShellSessionContext.DEFAULT_API_SCHEME

    reservation = session.CreateImmediateReservation(reservationName='tg regression tests', owner='admin',
                                                     durationInMinutes=60)
    reservation_id = reservation.Reservation.Id

    session.AddResourcesToReservation(reservationId=reservation_id, resourcesFullPath=ports)

    shell_attributes = attributes if type(attributes) is list else []
    session.AddServiceToReservation(reservationId=reservation_id,
                                    serviceName=controller,
                                    alias=controller,
                                    attributes=shell_attributes)
    service = session.GetReservationDetails(reservation_id).ReservationDescription.Services[0]

    context.resource = ResourceContextDetails()
    context.resource.name = service.ServiceName
    context.resource.attributes = attributes

    context.reservation = ReservationContextDetails()
    context.reservation.reservation_id = reservation_id
    context.reservation.owner_user = reservation.Reservation.Owner
    context.reservation.domain = reservation.Reservation.DomainName

    return context


def end_reservation(session, reservation_id):
    session.EndReservation(reservation_id)
    while session.GetReservationDetails(reservation_id).ReservationDescription.Status != 'Completed':
        time.sleep(1)
    session.DeleteReservation(reservation_id)
