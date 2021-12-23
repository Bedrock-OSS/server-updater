from subprocess import run
from actions.common import get_name_and_org, get_process_config
from flask import request

def set_status():
    if not "id" in request.form and 'status' in request.form: return "Bad request", 400
    id, status = request.form['id'], request.form['status']
    if(id == 'bedrock-oss:server-updater'):
        return "The server updater cannot be stopped", 400
    name, org = get_name_and_org(id)
    if(status):
        if start_project(name):
            return "Started", 200
        else:
            return "Project misconfigured", 500
    else: 
        if stop_project(name):
            return "Stopped", 200
        else:
            return "Project misconfigured", 500

def start_project(name):
    data = get_process_config(name)
    if('run_process' in data):
        run(['systemctl', '--user', 'start', 'bedrock-oss:' + name])
    elif('run_docker' in data):
        run(['docker', 'run', '-d', '--name', 'bedrock-oss-' + name, 'bedrock-oss-' + name])
    else: return False
    return True

def stop_project(name):
    data = get_process_config(name)
    if('run_process' in data):
        run(['systemctl', '--user', 'stop', 'bedrock-oss:' + name])
    elif('run_docker' in data):
        run(['docker', 'stop', 'bedrock-oss-' + name])
        run(['docker', 'rm', 'bedrock-oss-' + name])
    else: return False
    return True
