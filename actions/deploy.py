from actions.common import get_name_and_org
from actions.query_status import get_systemctl_status, get_docker_status
from actions.common import startswitharr, currentlyUpdating, config, get_process_config
from flask import request
from subprocess import PIPE, run
from os import path, remove, _exit
import datetime
import threading
import json

def deploy():
    if validate_data(request.form):
        name = get_name_and_org(request.form['id'])
        if name in currentlyUpdating:
            return "Already deploying " + name, 202
        if(name == 'server-updater'):
            # Probably shouldn't be a thread
            threading.Thread(target=update_running_process, args=(name,)).start()
            return "Deploying", 202
        elif(check_process(name)):
            currentlyUpdating[name] = [202, "Processing"]
            threading.Thread(target=update_running_process, args=(name,)).start()
        elif(check_docker(name)):
            currentlyUpdating[name] = [202, "Processing"]
            threading.Thread(target=update_running_docker, args=(name,)).start()

        return "Deploying", 202
    else:
        return "Bad request", 400

def check_docker(name):
    return "run_docker" in get_process_config(name)

def check_process(name):
    return 'run_process' in get_process_config(name)

def validate_data(data):
    startswith = startswitharr(data['id'], config["whitelisted"])

    # print('Supplied secret: ' + data['secret'])
    # print('Org supplied: ' + startswith)
    return data['id'] and startswith and (data['id'][len(startswith):].strip() == 'server-updater' or path.isdir(path.join('repos', data['id'][len(startswith):].strip())))

def update_running_docker(name):    
    try:
        # get the docker status of the container
        status = get_docker_status('bedrock-oss-' + name)
        if(status):
            print('Stopping container')
            proc = run(['docker', 'stop', 'bedrock-oss-' + name], stdout=PIPE, stderr=PIPE)
            if(proc.returncode != 0):
                currentlyUpdating[name] = [500, "Error stopping container"]
                return
            proc = run(['docker', 'rm', 'bedrock-oss-' + name], stdout=PIPE, stderr=PIPE)
            if(proc.returncode != 0):
                currentlyUpdating[name] = [500, "Error removing container"]
                return
        if(not update_git(name)): return
        proc = run(['docker', 'build', '-t', 'bedrock-oss-' + name, '.'], cwd=path.join(path.dirname(path.realpath(__file__)), 'repos', name), stdout=PIPE, stderr=PIPE)
        if(proc.returncode != 0):
            currentlyUpdating[name] = [500, "Error building container"]
            return
        if(status):
            proc = run(['docker', 'run', '-d', '--name', 'bedrock-oss-' + name, 'bedrock-oss-' + name], cwd=path.join(path.dirname(path.realpath(__file__)), 'repos', name), stdout=PIPE, stderr=PIPE)
            if(proc.returncode != 0):
                currentlyUpdating[name] = [500, "Error running container"]
                return
    except Exception as e:
        print(e)
        currentlyUpdating[name] = [500, "Error: " + str(e)]
        return
    currentlyUpdating[name] = [200, "Success"]
        
def update_git(name):
    print('Running pull')
    proc = run(['git', 'pull'], cwd=path.join(path.dirname(path.realpath(__file__)), 'repos', name), stdout=PIPE, stderr=PIPE)
    if(proc.returncode != 0):
        currentlyUpdating[name] = [500, "Error pulling from git"]
        return False
    return True


def update_running_process(name):
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
        status = get_systemctl_status('bedrock-oss-' + name)
        if(status):
            print('Running stop')
            proc = run(['sudo', 'systemctl', 'stop', "bedrock-oss:" + name], stdout=PIPE, stderr=PIPE)
            if(proc.returncode != 0):
                currentlyUpdating[name] = [500, "Error stopping process"]
                return

        update_git(name)
        if(status):
            print('Running start')
            proc = run(['sudo', 'systemctl', 'start', "bedrock-oss:" + name], stdout=PIPE, stderr=PIPE)
            if(proc.returncode != 0):
                currentlyUpdating[name] = [500, "Error starting process"]
                return
        currentlyUpdating[name] = [200, "Success"]
        print(name + " updated at " + str(datetime.datetime.now()))
    except Exception as e:
        currentlyUpdating[name] = [500, "Unexpected error: " + str(e)]
