from actions.common import get_name_and_org
from actions.deploy import validate_data
from common import get_process_config, currentlyUpdating
from flask import request
from subprocess import PIPE, run
import re

def query_status():
    if not validate_data(request.form): return "Bad request", 400
    name, org = get_name_and_org(request.form['id'])
    if name in currentlyUpdating:
        return "Deploying", 200
    if name == 'server-updater':
        return "Running", 200
    data = get_process_config(name)
    running = False
    if('run_process' in data):
        running = get_systemctl_status(request.form["id"])
    elif('run_docker' in data):
        running = get_docker_status(org + '-' + name)
    return ("Running" if running else "Stopped"), 200

def get_systemctl_status(name):
    proc = run(['systemctl', 'status', name], stdout=PIPE, stderr=PIPE)
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
