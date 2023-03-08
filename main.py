from requests.auth import HTTPBasicAuth
import requests
import key
import os
import urllib3
urllib3.disable_warnings()
import json
import time

def poll():
    start_time = get_file_time()
    while(True):
        file_time = get_file_time()
        if start_time != file_time:
            update_chests()
            start_time = file_time
        time.sleep(60)
    
def get_file_time():
    filename = 'C:\Riot Games\League of Legends\lockfile'
    return os.stat(filename).st_mtime

def update_chests():
    data = get_existing_data()
    chest_data = get_chest()


file = open(filename)
fcontents = file.readline()
file.close()
print(fcontents)

fcontents = fcontents.split(':')

port = fcontents[2]
username = 'riot'
password = fcontents[3]
format = fcontents[4]

base_url = format+'://127.0.0.1:'+port
account_session = requests.Session()
account_session.auth = ('riot', password)

response = account_session.get(base_url+'/lol-collections/v1/inventories/chest-eligibility', verify=False)
chest_info = response.json()

datafile = open('data.json', 'r+')

data = json.load(datafile)

data['wzl7'] = 'test'

datafile.seek(0)
datafile.write(json.dumps(data))
datafile.truncate()

