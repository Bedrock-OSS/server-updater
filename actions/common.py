import json
from os import path

currentlyUpdating = {}
def startswitharr(s, arr):
    if(type(arr) is not list):
        return False
    for a in arr:
        if s.startswith(a + "/"):
            return a + "/"
    return False
config = {}
with open('config.json', 'r') as f:
    config = json.load(f)
    config["whitelisted"].append("Bedrock-OSS")

def get_process_config(id):
    with open(path.join('repos', id, 'server_config.json'), 'r') as f:
        data = json.load(f)
        return data

def get_name_and_org(id):
    org = startswitharr(id, config["whitelisted"])
    return id[len(org):].strip(), org