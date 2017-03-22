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
    if proxy is not None:
        api.set_proxy({"https": proxy})

    location = location.replace(" ", "")
    location = location.split(",")
    place0 = float(location[0])
    place1 = float(location[1])
    api.set_position(place0, place1, 0.0)
    if hash_key:
        key = hash_key
        api.activate_hash_server(key)
    loggedin = False
    while loggedin is False:
        try:
            api.set_authentication(provider='ptc', username=username, password=password)
        except:
            print 'set_authentication failed, trying again in a sec'
            time.sleep(random.uniform(2, 4))
            continue
        try:
            response = api.app_simulation_login()
        except:
            print 'app_simulation_login failed, trying again in a sec'
            time.sleep(random.uniform(2, 4))
            continue
        if response is None:
            print "Servers do not respond to login attempt. " + failMessage
            return
        loggedin = True
        print 'Logged in, now enter the loop'
    done = False
    while done is False:
        request = api.create_request()
        request.get_player(
            player_locale={'country': 'US',
                           'language': 'en',
                           'timezone': 'America/Denver'})
        try:
            response = request.call().get('responses', {})
        except:
            print 'Get_Player failed, trying again in a sec'
            time.sleep(random.uniform(2, 4))
            continue

        get_player = response.get('GET_PLAYER', {})
        tutorial_state = get_player.get(
            'player_data', {}).get('tutorial_state', [])
        time.sleep(random.uniform(2, 4))

        if 0 not in tutorial_state:
            time.sleep(random.uniform(1, 5))
            request = api.create_request()
            request.mark_tutorial_complete(tutorials_completed=0)
            print 'Sending 0 tutorials_completed (TOS acceptance)'
            try:
                request.call()
            except:
                print 'TOS acceptance failed, trying again in a sec'
                time.sleep(random.uniform(2, 4))
                continue

        if 1 not in tutorial_state:
            time.sleep(random.uniform(5, 12))
            request = api.create_request()
            request.set_avatar(player_avatar={
                'hair': random.randint(1, 5),
                'shirt': random.randint(1, 3),
                'pants': random.randint(1, 2),
                'shoes': random.randint(1, 6),
                'avatar': random.randint(0, 1),
                'eyes': random.randint(1, 4),
                'backpack': random.randint(1, 5)
            })
            try:
                request.call()
            except:
                print 'player_avater set failed, trying again in a sec'
                time.sleep(random.uniform(2, 4))
                continue

            time.sleep(random.uniform(0.3, 0.5))

            request = api.create_request()
            request.mark_tutorial_complete(tutorials_completed=1)
            print 'Sending 1 tutorials_completed'
            try:
                request.call()
            except:
                print 'tutorial_completed 1 failed, trying again in a sec'
                time.sleep(random.uniform(2, 4))
                continue

            time.sleep(random.uniform(0.5, 0.6))
            request = api.create_request()
            request.get_player_profile()
            print 'Fetching player profile'
            try:
                request.call()
            except:
                print 'Player profile fetch failed, trying again in a sec'
                time.sleep(random.uniform(2, 4))
                continue

            starter_id = None
            if 3 not in tutorial_state:
                time.sleep(random.uniform(1, 1.5))
                request = api.create_request()
                request.get_download_urls(asset_id=[
                    '1a3c2816-65fa-4b97-90eb-0b301c064b7a/1477084786906000',
                    'aa8f7687-a022-4773-b900-3a8c170e9aea/1477084794890000',
                    'e89109b0-9a54-40fe-8431-12f7826c8194/1477084802881000'])
                print 'Grabbing some game assets.'
                try:
                    request.call()
                except:
                    print 'Get assets failed, trying again in a sec'
                    time.sleep(random.uniform(2, 4))
                    continue

                time.sleep(random.uniform(1, 1.6))
                request = api.create_request()
                try:
                    request.call()
                except:
                    print 'After-Assets failed, trying again in a sec'
                    time.sleep(random.uniform(2, 4))
                    continue

                time.sleep(random.uniform(6, 13))
                request = api.create_request()
                starter = random.choice((1, 4, 7))
                request.encounter_tutorial_complete(pokemon_id=starter)
                print 'Catching the starter'
                try:
                    request.call()
                except:
                    print 'Starter_catch failed, trying again in a sec'
                    time.sleep(random.uniform(2, 4))
                    continue

                time.sleep(random.uniform(0.5, 0.6))
                request = api.create_request()
                request.get_player(
                    player_locale={
                        'country': 'US',
                        'language': 'en',
                        'timezone': 'America/Denver'})
                try:
                    responses = request.call().get('responses', {})
                except:
                    print 'Get_Player failed, trying again in a sec'
                    time.sleep(random.uniform(2, 4))
                    continue

                inventory = responses.get('GET_INVENTORY', {}).get(
                    'inventory_delta', {}).get('inventory_items', [])
                for item in inventory:
                    pokemon = item.get('inventory_item_data', {}).get('pokemon_data')
                    if pokemon:
                        starter_id = pokemon.get('id')

            if 4 not in tutorial_state:
                time.sleep(random.uniform(5, 12))
                request = api.create_request()
                request.claim_codename(codename=username)
                print 'Claiming codename'
                try:
                    request.call()
                except:
                    print 'Claim Codename failed, trying again in a sec'
                    time.sleep(random.uniform(2, 4))
                    continue

                time.sleep(random.uniform(1, 1.3))
                request = api.create_request()
                request.mark_tutorial_complete(tutorials_completed=4)
                print 'Sending 4 tutorials_completed'
                try:
                    request.call()
                except:
                    print '4th tutorial failed, trying again in a sec'
                    time.sleep(random.uniform(2, 4))
                    continue

                time.sleep(0.1)
                request = api.create_request()
                request.get_player(
                    player_locale={
                        'country': 'US',
                        'language': 'en',
                        'timezone': 'America/Denver'})
                try:
                    request.call()
                except:
                    print 'Get_Player failed, trying again in a sec'
                    time.sleep(random.uniform(2, 4))
                    continue

            if 7 not in tutorial_state:
                time.sleep(random.uniform(4, 10))
                request = api.create_request()
                request.mark_tutorial_complete(tutorials_completed=7)
                print 'Sending 7 tutorials_completed'
                try:
                    request.call()
                except:
                    print '7th tutorial failed, trying again in a sec'
                    time.sleep(random.uniform(2, 4))
                    continue

            if starter_id:
                time.sleep(random.uniform(3, 5))
                request = api.create_request()
                request.set_buddy_pokemon(pokemon_id=starter_id)
                print 'Setting buddy pokemon'
                try:
                    request.call()
                except:
                    print 'Buddy set failed, trying again in a sec'
                    time.sleep(random.uniform(2, 4))
                    continue
                done = True
                time.sleep(random.uniform(0.8, 1.8))

            # Sleeping before we start scanning to avoid Niantic throttling.
            print 'Finished TOS and tutorial. Sleeping.'
            done = True
            time.sleep(random.uniform(1, 2))
        return True


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
