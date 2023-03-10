from requests.auth import HTTPBasicAuth
import requests
import key
import os
import urllib3
urllib3.disable_warnings()
import json
import time


filename = 'C:\Riot Games\League of Legends\lockfile'
username = 'riot'
account_session = None
base_url = None
data = None

def poll():
    start_time = get_file_time()
    while(True):
        file_time = get_file_time()
        if start_time != file_time:
            update_data_file()
            start_time = file_time
        time.sleep(60)
    
def get_file_time():
    global filename
    return os.stat(filename).st_mtime

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
    datafile = open('data.json', 'r')
    data = json.load(datafile)
    datafile.close()

def save_data():
    global data
    datafile = open('data.json', 'w')
    datafile.write(json.dumps(data))
    datafile.close()

def main():
    get_data()

if __name__ == '__main__':
    main()
