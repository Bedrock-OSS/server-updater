from actions.common import get_name_and_org
from actions.common import get_process_config, currentlyUpdating, validate_data
from flask import request
from subprocess import PIPE, run
import re

def query_status():
    if not validate_data(request.form): return "Bad request", 400
    name, org = get_name_and_org(request.form['id'])
    return get_status(name, org), 200

def get_status(name, org):
    if name in currentlyUpdating and currentlyUpdating[name][0] != 200:
        text = currentlyUpdating[name][1]
        if currentlyUpdating[name][0] != 202: del currentlyUpdating[name]
        return text
    if name == 'server-updater':
        return "Running"
    data = get_process_config(name)
    # print(data)
    running = False
    if('run_process' in data):
        running = get_systemctl_status(org + ':' + name)
    elif('run_docker' in data):
        running = get_docker_status(org + '-' + name)
    return "Running" if running else "Stopped"

def get_systemctl_status(name):
    proc = run(['systemctl', '--user', 'status', name], stdout=PIPE, stderr=PIPE)
    if(proc.returncode == 0):
        return True
    else:
        return False

def get_docker_status(name):
    proc = run(['docker', 'ps', '-a', '--filter', 'name=^/' + name + '$', '--format', '\{{.Names}}: \{{.Status}}'], stdout=PIPE, stderr=PIPE)
    out = proc.stdout.decode('utf-8')
    print(out)
    if(name in out):
        match = re.search('\\\\' + name + ': \\\(\w+)', out)
        return match.group(1) == 'Up' if match else False
    else:
        return False
