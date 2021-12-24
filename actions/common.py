import json
from os import path

currentlyUpdating = {}
def startswitharr(s, arr):
    if(type(arr) is not list):
        return False
    for a in arr:
        if s.lower().startswith(a + ":"):
            return a + ":"
    return False
config = {}
with open('config.json', 'r') as f:
    config = json.load(f)
    config["whitelisted"].append("bedrock-oss")

def get_process_config(id):
    try:
        with open(path.join('repos', id, 'server_config.json'), 'r') as f:
            data = json.load(f)
            return data
    except:
        return {}

def get_name_and_org(id):
    org = startswitharr(id.lower(), config["whitelisted"])
    return id[len(org):].strip(), org

def validate_data(data):
    startswith = startswitharr(data['id'], config["whitelisted"])
    return data['id'] and startswith and (data['id'][len(startswith):].strip() == 'server-updater' or path.isdir(path.join('repos', data['id'][len(startswith):].strip())))
