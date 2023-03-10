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
    

start_time = 0
filename = 'C:\Riot Games\League of Legends\lockfile'
if is_unix():
    filename = '/Applications/League of Legends.app/Contents/LoL/lockfile'
else:
    start_time = get_file_time()
username = 'riot'
account_session = None
base_url = None
data = {}


def poll():
    global start_time
    while(True):
        file_time = get_file_time()
        if start_time != file_time:
            update_data_file()
            start_time = file_time
        time.sleep(60)


def account_active():
    if is_unix():
        return os.path.isfile(filename)
    else:
        global start_time
        file_time = get_file_time()
        last_time = start_time
        start_time = file_time
        return last_time != file_time


def update_data_file():
    global data
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


def update_data():
    for user in data:
        if get_current_time() > data[user]["nextChestRechargeTime"]:
            print('calculate number of chests available')
            
            
def main():
    get_data()
    if account_active():
        parse_lock()
        data[get_name()] = get_chest_info()
        save_data()
    else:
        update_data()

if __name__ == '__main__':
    main()
