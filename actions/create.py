import os
from subprocess import PIPE, run
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
