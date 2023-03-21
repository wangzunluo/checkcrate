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


def poll():
    while(True):
        update_data_file()
        time.sleep(60*5)


def account_active():
    return os.path.isfile(filename)


def update_data_file():
    global data
    if account_active:
        name = get_name()
        data[name] = get_chest_info()
        save_data()


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


def get_name():
    global account_session
    response = account_session.get(base_url+'/lol-summoner/v1/current-summoner', verify=False)
    response = response.json()
    return response['displayName']


def get_chest_info():
    global account_session
    response = account_session.get(base_url+'/lol-collections/v1/inventories/chest-eligibility', verify=False)
    return response.json()


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
    get_current_time()
    print('calculate number of chests available')
            
            
def main():
    poll()

if __name__ == '__main__':
    main()
