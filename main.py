from requests.auth import HTTPBasicAuth
import requests
import os
import urllib3
urllib3.disable_warnings()
import json
import time


def is_unix():
    return os.name == 'posix'


def get_file_time():
    global filename
    return os.stat(filename).st_mtime
    


filename = 'C:\Riot Games\League of Legends\lockfile'
if is_unix():
    filename = '/Applications/League of Legends.app/Contents/LoL/lockfile'

username = 'riot'
account_session = None
base_url = None
data = {}
max_length_user = 0

def poll():
    while(True):
        update_data_file()
        return
        time.sleep(60*5)


def account_active():
    return os.path.isfile(filename)


def update_data_file():
    global data
    global max_length_user
    if account_active():
        parse_lock()
        name = get_name()
        data[name] = get_chest_info()
        data[name]['missions'] = get_mission_info()
        save_data()
        
    for user in data:
        gained, time_string = calculate_chest(data[user]['nextChestRechargeTime'])
        earnable = data[user]['earnableChests'] + gained
        if earnable > data[user]['maximumChests']:
            earnable = data[user]['maximumChests']
        print('{0: <{luser}} {1} chest(s) available. Next chest available: '.format(user, earnable, luser=max_length_user)+time_string)
        if 'missions' in data[user]:
            for mission in data[user]['missions']:
                print('{0: <{luser}} {1}: Objectives:'.format('', mission['name'], luser=max_length_user))
                for obj in mission['objectives']:
                    if 'Earn points from time spent' in obj['description']:
                        obj['description'] = 'Earn points from time spent playing and winning games'
                    print('{0: <{luser}} {1}: {2}/{3}'.format('', obj['description'], obj['progress']['currentProgress'], obj['progress']['totalCount'], luser=max_length_user))
                print('{0: <{luser}} Rewards: '.format('', luser=max_length_user))
                for reward in mission['rewards']:
                    print('{0: <{luser}} {1}'.format('', reward['description'], luser=max_length_user))
                time_to_expire = calculate_time_string(mission['endTime'], window=True)
                print('{0: <{luser}} Time remaining: {1}'.format('', time_to_expire, luser=max_length_user))
        


def read_lock():
    global filename
    file = open(filename)
    fcontents = file.readline()
    file.close()
    print(fcontents)
    return fcontents


def parse_lock():
    global base_url
    global account_session
    lock_content = read_lock().split(':')
    port = lock_content[2]
    password = lock_content[3]
    format = lock_content[4]
    base_url = format+'://127.0.0.1:'+port
    account_session = requests.Session()
    account_session.auth = (username, password)

def get_client(url):
    global account_session
    response = account_session.get(base_url+url, verify=False)
    return response.json()


def get_name():
    return get_client('/lol-summoner/v1/current-summoner')['displayName']


def get_chest_info():
    return get_client('/lol-collections/v1/inventories/chest-eligibility')


def get_mission():
    return get_client('/lol-missions/v1/missions')


def get_data():
    global data
    if not os.path.isfile('./data.json'):
        save_data()
    datafile = open('data.json', 'r')
    data = json.load(datafile)
    datafile.close()


def save_data():
    global data
    datafile = open('data.json', 'w')
    datafile.write(json.dumps(data))
    datafile.close()


def get_current_time():
    return int(str(time.time()).replace('.', '')[:13])


def calculate_chest(next_time):
    current = get_current_time()
    time_string = calculate_time_string(next_time)
    if current < next_time:
        return (0, time_string)
    diff = int(str(current)[:10])-int(str(next_time)[:10])
    week = 604800
    available = diff // week + 1
    return (available, time_string)

            
def calculate_time_string(next_time, window=False):
    week = 604800
    current = get_current_time()
    diff = int(str(current)[:10])-int(str(next_time)[:10])
    if diff < 0:
        diff *= -1
        mr = diff % week
        time_to_chest = mr
    else:
        mr = diff % week
        time_to_chest = week - mr
    gm = time.gmtime(time_to_chest)
    hms = time.strftime('%H hours: %M minutes: %S seconds', gm)
    if window:
        days = str(diff // 86400)+' days : '
    else:
        days = str(int(time.strftime('%d', gm))-1)+' days : '
    time_string = days + hms
    return time_string


def get_max_username():
    global max_length_user
    global data
    for user in data:
        if len(user) > max_length_user:
            max_length_user = len(user) + 1


def get_mission_info():
    missions = get_mission()
    available = []
    for mission in missions:
        if mission['status'] not in ['COMPLETED', 'DUMMY'] and \
        'faeriecourt' in mission['internalName'].lower() and \
        mission['missionType'] not in ['REPEATING']:
            available.append(mission)
    cleaned_data = []
    for mission in available:
        cleaned_data.append({
            'name': mission['internalName'],
            'objectives': mission['objectives'],
            'rewards': mission['rewards'],
            'endTime': mission['endTime']
        })
    return cleaned_data
        
    

            
def main():
    get_data()
    get_max_username()
    poll()


if __name__ == '__main__':
    main()
