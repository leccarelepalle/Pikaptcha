import time
import string
import random
from uuid import uuid4
from pgoapi import PGoApi
from pgoapi.utilities import f2i
from pgoapi import utilities as util
from pgoapi.exceptions import AuthException, ServerSideRequestThrottlingException, NotLoggedInException

def accept_tos(username, password, location, proxy, hash_key):
    try:
        accept_tos_helper(username, password, location, proxy, hash_key)
    except ServerSideRequestThrottlingException as e:
        print('Server side throttling, Waiting 10 seconds.')
        time.sleep(10)
        accept_tos_helper(username, password, location, proxy, hash_key)
    except NotLoggedInException as e1:
        print('Could not login, Waiting for 10 seconds')
        time.sleep(10)
        accept_tos_helper(username, password, location, proxy, hash_key)

def accept_tos_helper(username, password, location, proxy, hash_key):
    print "Trying to accept Terms of Service for {}.".format(username)
    failMessage = "Maybe the HTTPS proxy is not working? {} did not accept Terms of Service.".format(username)

    device_info = generate_device_info()
    api = PGoApi(device_info=device_info)
    if proxy != None:
        api.set_proxy({"https":proxy})

    location = location.replace(" ", "")
    location = location.split(",")
    place0 = float(location[0])
    place1 = float(location[1])
    api.set_position(place0, place1, 0.0)
    if hash_key:
        key = hash_key
        api.activate_hash_server(key)
    api.set_authentication(provider = 'ptc', username = username, password = password)
    response = api.app_simulation_login()
    if response == None:
        print "Servers do not respond to login attempt. " + failMessage
        return

    time.sleep(1)
    req = api.create_request()
    req.mark_tutorial_complete(tutorials_completed = 0, send_marketing_emails = False, send_push_notifications = False)
    response = req.call()
    if response == None:
        print "Servers do not respond to accepting the ToS. " + failMessage
        return

    print('Accepted Terms of Service for {}'.format(username))


# Generate random device info.
# Original by Noctem.
IPHONES = {'iPhone5,1': 'N41AP',
           'iPhone5,2': 'N42AP',
           'iPhone5,3': 'N48AP',
           'iPhone5,4': 'N49AP',
           'iPhone6,1': 'N51AP',
           'iPhone6,2': 'N53AP',
           'iPhone7,1': 'N56AP',
           'iPhone7,2': 'N61AP',
           'iPhone8,1': 'N71AP',
           'iPhone8,2': 'N66AP',
           'iPhone8,4': 'N69AP',
           'iPhone9,1': 'D10AP',
           'iPhone9,2': 'D11AP',
           'iPhone9,3': 'D101AP',
           'iPhone9,4': 'D111AP'}


def generate_device_info():
    device_info = {'device_brand': 'Apple', 'device_model': 'iPhone',
                   'hardware_manufacturer': 'Apple',
                   'firmware_brand': 'iPhone OS'}
    devices = tuple(IPHONES.keys())

    ios8 = ('8.0', '8.0.1', '8.0.2', '8.1', '8.1.1',
            '8.1.2', '8.1.3', '8.2', '8.3', '8.4', '8.4.1')
    ios9 = ('9.0', '9.0.1', '9.0.2', '9.1', '9.2', '9.2.1',
            '9.3', '9.3.1', '9.3.2', '9.3.3', '9.3.4', '9.3.5')
    ios10 = ('10.0', '10.0.1', '10.0.2', '10.0.3', '10.1', '10.1.1')

    device_info['device_model_boot'] = random.choice(devices)
    device_info['hardware_model'] = IPHONES[device_info['device_model_boot']]
    device_info['device_id'] = uuid4().hex

    if device_info['hardware_model'] in ('iPhone9,1', 'iPhone9,2',
                                         'iPhone9,3', 'iPhone9,4'):
        device_info['firmware_type'] = random.choice(ios10)
    elif device_info['hardware_model'] in ('iPhone8,1', 'iPhone8,2',
                                           'iPhone8,4'):
        device_info['firmware_type'] = random.choice(ios9 + ios10)
    else:
        device_info['firmware_type'] = random.choice(ios8 + ios9 + ios10)

    return device_info
