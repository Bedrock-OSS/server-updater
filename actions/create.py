import os
from subprocess import PIPE, run
from actions.common import get_process_config
from flask import request

def create():
    if 'id' not in request.form:
        return 'Invalid request', 400
    # Tiny honestly unnecessary check (because having the 
    # secret should identify the user as trusted anyway)
    if(' ' in request.form['id']):
        return 'Invalid request', 400
    [org, name] = request.form['id'].split(':')
    run(['git', 'clone', 'https://github.com/%s/%s' % (org, name)], cwd='/home/ubuntu/oss/repos')
    data = get_process_config(name)
    if 'run_process' in data:
        create_systemctl_process(name, data['run_process'], False)
    elif 'run_docker' in data:
        create_docker_process(name, data['run_docker'], False)
    return 'Ok', 200


def create_systemctl_process(id, command, start):
    systemctl_file = """
    [Unit]
    Description=Runner for %s
    After=network.target

    [Service]
    Type=simple
    ExecStart=%s
    Restart=always
    RestartSec=1
    WorkingDirectory=/home/%s/oss/repos/%s
    """ % (id, command, os.getlogin(), id)
    if os.path.isfile('/home/%s/.config/systemd/user/bedrock-oss:' + id + '.service'):
        return False
    with open('/home/%s/.config/systemd/user/bedrock-oss:%s.service' % (os.getlogin(), id), 'w') as f:
        f.write(systemctl_file)
    run(['systemctl', '--user', 'daemon-reload'])
    run(['systemctl', '--user', 'enable', 'bedrock-oss-' + id])
    if start:
        run(['systemctl', '--user', 'start', id])
    return True
    
def create_docker_process(id, dockerfile, start):
    if not os.path.isfile('/home/%s/oss/repos/%s/%s' % (os.getlogin(), id, dockerfile)):
        return False
    if run(['docker', 'build', '-t', 'bedrock-oss-' + id, dockerfile]).returncode != 0:
        return False
    if start:
        run(['docker', 'run', '-d', '--name', 'bedrock-oss-' + id, ' bedrock-oss-' + id])
    return True
