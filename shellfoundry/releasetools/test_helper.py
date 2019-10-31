import inspect
from os import path
import time
import yaml
import xml.etree.ElementTree as ET

from cloudshell.shell.core.driver_context import (ResourceCommandContext, ResourceContextDetails,
                                                  ReservationContextDetails, ConnectivityContext, InitCommandContext)
from cloudshell.api.cloudshell_api import CloudShellAPISession, ResourceAttributesUpdateRequest
from cloudshell.shell.core.session.cloudshell_session import CloudShellSessionContext


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


def get_namespace_from_cloudshell_config():

    test_name = inspect.stack()[1][1]
    f = path.join(path.dirname(path.dirname(test_name)), 'shell-definition.yaml')
    with open(f, 'r') as f:
        doc = yaml.load(f)
    return list(doc['node_types'].keys())[0].split('.')[-1]


def create_session_from_deployment():

    test_name = inspect.stack()[1][1]
    deployment = path.join(path.dirname(path.dirname(test_name)), 'deployment.xml')
    root = ET.parse(deployment).getroot()
    host = root.find('serverRootAddress').text
    username = root.find('username').text
    password = root.find('password').text
    domain = root.find('domain').text

    return CloudShellAPISession(host, username, password, domain)


def create_autoload_context_2g(session, model, address, attributes):

    connectivity = ConnectivityContext(session.host, '8029', '9000', session.token_id, '9.1',
                                       CloudShellSessionContext.DEFAULT_API_SCHEME)
    resource = ResourceContextDetails(id='ididid', name='testing', fullname='Testing/testing', type='Resource', address=address,
                                      model=model, family='CS_TrafficGeneratorChassis', description='',
                                      attributes=attributes, app_context='', networks_info='',
                                      shell_standard='cloudshell_traffic_generator_chassis_standard',
                                      shell_standard_version='1_0_3')
    context = InitCommandContext(connectivity, resource)
    return context


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

    session.AddResourcesToReservation(reservationId=reservation_id, resourcesFullPath=ports)

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


def create_autoload_resource_2g(session, model, address, name, attributes):
    resource = session.CreateResource(resourceFamily='CS_TrafficGeneratorChassis',
                                      resourceModel=model,
                                      resourceName=name,
                                      resourceAddress=address,
                                      folderFullPath='',
                                      parentResourceFullPath='',
                                      resourceDescription='should be removed after test')
    session.UpdateResourceDriver(resource.Name, model)
    session.SetAttributesValues(ResourceAttributesUpdateRequest(resource.Name, attributes))
    return resource


def end_reservation(session, reservation_id):
    session.EndReservation(reservation_id)
    while session.GetReservationDetails(reservation_id).ReservationDescription.Status != 'Completed':
        time.sleep(1)
    session.DeleteReservation(reservation_id)
