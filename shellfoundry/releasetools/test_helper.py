import inspect
import os
from os import path
import time
import yaml
import xml.etree.ElementTree as ET

from cloudshell.shell.core.driver_context import (ResourceCommandContext, ResourceContextDetails,
                                                  ReservationContextDetails, ConnectivityContext, InitCommandContext)
from cloudshell.api.cloudshell_api import CloudShellAPISession, ResourceAttributesUpdateRequest
from cloudshell.api.common_cloudshell_api import CloudShellAPIError
from cloudshell.shell.core.session.cloudshell_session import CloudShellSessionContext

from cloudshell.helpers.scripts.cloudshell_dev_helpers import attach_to_cloudshell_as
import cloudshell.helpers.scripts.cloudshell_scripts_helpers as script_help




#
# 1st gen helpers used by IxChariot, Avalanche and Xena controller shells. Remove once all controllers are upgraded.
#

def create_session_from_cloudshell_config():

    test_name = inspect.stack()[1][1]
    f = path.join(path.dirname(path.dirname(test_name)), 'cloudshell_config.yml')
    with open(f, 'r') as f:
        doc = yaml.load(f)
    username = doc['install']['username']
    password = doc['install']['password']
    domain = doc['install']['domain']
    host = doc['install']['host']

    return CloudShellAPISession(host, username, password, domain)

#
# 2nd generation helers.
#

def get_deployment_root():

    index = 1
    test_name = inspect.stack()[index][1]
    while test_name == __file__:
        index += 1
        test_name = inspect.stack()[index][1]
    shell_dir = path.dirname(path.dirname(test_name))
    if not path.exists(shell_dir + '/deployment.xml'):
        shell_dir = path.dirname(shell_dir)
    deployment = shell_dir + '/deployment.xml'
    return ET.parse(deployment).getroot()


def get_credentials_from_deployment():

    root = get_deployment_root()
    host = root.find('serverRootAddress').text
    username = root.find('username').text
    password = root.find('password').text
    domain = root.find('domain').text
    return host, username, password, domain


def create_topology_reservation(session, topology_path, reservation_name='tg regression tests', global_inputs=[]):

    _, owner, _, _ = get_credentials_from_deployment()
    try:
        reservation = session.CreateImmediateTopologyReservation(reservationName=reservation_name,
                                                                 topologyFullPath=topology_path,
                                                                 globalInputs=global_inputs,
                                                                 owner=owner, durationInMinutes=60)
    except CloudShellAPIError as e:
        reservations = session.GetCurrentReservations(reservationOwner='admin')
        for reservation in reservations.Reservations:
            if reservation.Name == 'tg regression tests':
                session.EndReservation(reservation.Id)
        time.sleep(2)
        reservation = session.CreateImmediateTopologyReservation(reservationName=reservation_name,
                                                                 topologyFullPath=topology_path,
                                                                 globalInputs=global_inputs,
                                                                 owner=owner, durationInMinutes=60)
    return reservation


def create_reservation(session, reservation_name='tg regression tests'):

    _, owner, _, _ = get_credentials_from_deployment()
    reservations = session.GetCurrentReservations(reservationOwner=owner)
    for reservation in [r for r in reservations.Reservations if r.Name == reservation_name]:
        session.EndReservation(reservation.Id)
    reservation = session.CreateImmediateReservation(reservationName=reservation_name, owner=owner,
                                                     durationInMinutes=60)
    return reservation


def create_session_from_deployment():
    return CloudShellAPISession(*get_credentials_from_deployment())


def end_reservation(session, reservation_id):
    try:
        session.EndReservation(reservation_id)
        while session.GetReservationDetails(reservation_id).ReservationDescription.Status != 'Completed':
            time.sleep(1)
        session.DeleteReservation(reservation_id)
    except Exception as _:
        pass


def create_init_command_context(session, family, model, address, attributes, type):
    """
    :param CloudShellAPISession session:
    :param family:
    :param model:
    :param address:
    :param type: Resource or Service
    :param attributes:
    :return: Dict of attributes
    """
    connectivity = ConnectivityContext(session.host, '8029', '9000', session.token_id, '9.1',
                                       CloudShellSessionContext.DEFAULT_API_SCHEME)
    resource = ResourceContextDetails(id='ididid', name='testing', fullname='Testing/testing',
                                      address=address, family=family, model=model, attributes=attributes, type=type,
                                      app_context='', networks_info='', description='',
                                      shell_standard='', shell_standard_version='')
    context = InitCommandContext(connectivity, resource)
    return context


def create_service_command_context(session, service_name, alias=None, attributes=[]):
    """

    :param CloudShellAPISession session:
    :param service_name:
    :param alias:
    :param attributes:
    :return:
    """
    reservation = create_reservation(session)
    reservation_id = reservation.Reservation.Id
    if not alias:
        alias = service_name
    session.AddServiceToReservation(reservationId=reservation_id,
                                    serviceName=service_name,
                                    alias=alias,
                                    attributes=attributes)

    os.environ['DEVBOOTSTRAP'] = 'True'
    debug_attach_from_deployment(reservation_id, service_name=service_name)
    reservation = script_help.get_reservation_context_details()
    resource = script_help.get_resource_context_details()

    connectivity = ConnectivityContext(session.host, '8029', '9000', session.token_id, '9.1',
                                       CloudShellSessionContext.DEFAULT_API_SCHEME)

    context = ResourceCommandContext(connectivity, resource, reservation, [])
    return context


def create_resource_command_context(session, resource_path):

    reservation = create_reservation(session)
    reservation_id = reservation.Reservation.Id
    session.AddResourcesToReservation(reservationId=reservation_id, resourcesFullPath=[resource_path])

    os.environ['DEVBOOTSTRAP'] = 'True'
    debug_attach_from_deployment(reservation_id, resource_path)
    reservation = script_help.get_reservation_context_details()
    resource = script_help.get_resource_context_details()

    connectivity = ConnectivityContext(session.host, '8029', '9000', session.token_id, '9.1',
                                       CloudShellSessionContext.DEFAULT_API_SCHEME)

    context = ResourceCommandContext(connectivity, resource, reservation, [])
    return context


def create_autoload_resource(session, family, model, address, name, attributes):
    """
    :param CloudShellAPISession session:
    :param family:
    :param model:
    :param address:
    :param name:
    :param attributes:
    :return:
    """
    existing_resource = [r for r in session.GetResourceList().Resources if r.Name == name]
    if existing_resource:
        session.DeleteResource(existing_resource[0].Name)
    resource = session.CreateResource(resourceFamily=family,
                                      resourceModel=model,
                                      resourceName=name,
                                      resourceAddress=address,
                                      folderFullPath='',
                                      parentResourceFullPath='',
                                      resourceDescription='should be removed after test')
    session.UpdateResourceDriver(resource.Name, model)
    session.SetAttributesValues(ResourceAttributesUpdateRequest(resource.Name, attributes))
    return resource


def create_command_context_2g(session, ports, controller, attributes):

    """ Create command context from scratch.

    :param session: CloudShell API session
    :type session: cloudshell.api.cloudshell_api.CloudShellAPISession
    :param controller: TG controller name
    :param ports: list of TG port resources address ['chassis/module/port',...]
    :param attributes: for driver tests - dictionary {name: value} of TG controller attributes
                       for shell tests - list [AttributeNameValue] of TG controller attributes
    """

    connectivity = ConnectivityContext(session.host, '8029', '9000', session.token_id, '9.1',
                                       CloudShellSessionContext.DEFAULT_API_SCHEME)

    reservation = session.CreateImmediateReservation(reservationName='tg regression tests', owner='admin',
                                                     durationInMinutes=60)
    reservation_id = reservation.Reservation.Id

    # session.AddResourcesToReservation(reservationId=reservation_id, resourcesFullPath=ports)

    shell_attributes = attributes if type(attributes) is list else []
    session.AddServiceToReservation(reservationId=reservation_id,
                                    serviceName=controller,
                                    alias=controller,
                                    attributes=shell_attributes)
    service = session.GetReservationDetails(reservation_id).ReservationDescription.Services[0]

    resource = ResourceContextDetails(id='ididid', name= service.ServiceName, fullname='', type='Service', address='',
                                      model='', family='', description='', attributes=attributes, app_context='',
                                      networks_info='',
                                      shell_standard='cloudshell_traffic_generator_controller_standard',
                                      shell_standard_version='2_0_0')

    reservation = ReservationContextDetails(environment_name='', environment_path='',
                                            domain=reservation.Reservation.DomainName, description='',
                                            owner_user=reservation.Reservation.Owner, owner_email='',
                                            reservation_id=reservation_id)

    context = ResourceCommandContext(connectivity, resource, reservation, [])
    return context


def debug_attach_from_deployment(reservation_id, resource_name=None, service_name=None):

    host, username, password, domain = get_credentials_from_deployment()
    attach_to_cloudshell_as(
        server_address=host,
        user=username,
        password=password,
        reservation_id=reservation_id,
        domain=domain,
        resource_name=resource_name,
        service_name=service_name
    )


# Should I move to pylgi? Should I create a general test package that can be extended?
cisco_mac = {'mac': '48d3.4373.32eb', 'ip': ('10.15.91.43','EB/48D3437332EB')}
