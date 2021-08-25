import datetime
from flask import Flask, request
from os import path, remove, _exit
from subprocess import PIPE, run
import threading
import json

config = {}
with open('config.json', 'r') as f:
    config = json.load(f)
    config["whitelisted"].append("Bedrock-OSS")

app = Flask(__name__)

currentlyUpdating = {}

@app.route('/deploy', methods=['POST'])
def handle_deploy_request():
    if validate_data(request.form):
        org = startswitharr(request.form['id'], config['whitelisted'])
        name = request.form['id'][len(org):].strip()
        if name in currentlyUpdating:
            if(name == 'server-updater'):
                print('Update updater confirmed!')
            ret = currentlyUpdating[name]
            if currentlyUpdating[name][0] in [500, 200]:
                del currentlyUpdating[name]
            return ret[1], ret[0]
        currentlyUpdating[name] = [202, "Processing"]
        
        threading.Thread(target=update_repo, args=(name,)).start()

        return "Deploying", 202
    else:
        return "Invalid request", 500

def update_repo(name):
    if(name == 'server-updater'):
        print('Updating the updater', flush=True)
        try:
            with open('update', 'w') as f:
                f.write('')
            proc = run(['git', 'pull'], cwd=path.join(path.dirname(path.realpath(__file__))), stdout=PIPE, stderr=PIPE)
            if(proc.returncode != 0):
                currentlyUpdating['server-updater'] = [500, "Error pulling from git"]
                print("Failed with git error", flush=True)
                remove('update')
                return
            print('Pulled from git, restarting')
        except Exception as e:
            currentlyUpdating['server-updater'] = [500, "Unexpected error: " + str(e)]
            print("Failed with unexpected error", flush=True)
            remove('update')
            return
        _exit(1) # systemctl will restart the updater

    try:
        print('Running stop')
        proc = run(['sudo', 'systemctl', 'stop', "bedrock-oss:" + name], stdout=PIPE, stderr=PIPE)
        if(proc.returncode != 0):
            currentlyUpdating[name] = [500, "Error stopping process"]
            return
        print('Running pull')
        proc = run(['git', 'pull'], cwd=path.join(path.dirname(path.realpath(__file__)), 'repos', name), stdout=PIPE, stderr=PIPE)
        if(proc.returncode != 0):
            currentlyUpdating[name] = [500, "Error pulling from git"]
            return
        print('Running start')
        proc = run(['sudo', 'systemctl', 'start', "bedrock-oss:" + name], stdout=PIPE, stderr=PIPE)

        if(proc.returncode != 0):
            currentlyUpdating[name] = [500, "Error starting process"]
            return
        currentlyUpdating[name] = [200, "Success"]
        print(name + " updated at " + str(datetime.datetime.now()))
    except Exception as e:
        currentlyUpdating[name] = [500, "Unexpected error: " + str(e)]

def validate_data(data):
    startswith = startswitharr(data['id'], config["whitelisted"])

    print('Supplied secret: ' + data['secret'])
    print('Org supplied: ' + startswith)
    return data['secret'] == config['secret'] and data['id'] and startswith and (data['id'][len(startswith):].strip() == 'server-updater' or path.isdir(path.join('repos', data['id'][len(startswith):].strip())))

def startswitharr(s, arr):
    for a in arr:
        if s.startswith(a + "/"):
            return a + "/"
    return False

try:
    remove('update')
    currentlyUpdating['server-updater'] = [200, "Success"]
except OSError:
    pass
