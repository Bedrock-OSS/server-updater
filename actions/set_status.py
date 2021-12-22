from flask imoprt request

def set_status():
    if not "name" in request.form and 'status' in request.form: return "Bad request", 400
    name, status = request.form['name'], request.form['status']
    if(name == 'server-updater'):
        return "The server updater cannot be stopped", 400
    data = get_process_config(name)
    if(status) return ("Started", 200) if start_project(name) else ("Project misconfigured", 500)
    else return ("Stopped", 200) if stop_project(name) else ("Project misconfigured", 500)

def start_project(name):
    data = get_process_config(name)
    if('run_process' in data):
        run(['systemctl', '--user', 'start', 'bedrock-oss:' + name])
    elif('run_docker' in data):
        run(['docker', 'run', '-d', '--name', 'bedrock-oss-' + name, 'bedrock-oss-' + name])
    else return False
    return True

def stop_project(name):
    data = get_process_config(name)
    if('run_process' in data):
        run(['systemctl', '--user', 'stop', 'bedrock-oss:' + name])
    elif('run_docker' in data):
        run(['docker', 'stop', 'bedrock-oss-' + name])
        run(['docker', 'rm', 'bedrock-oss-' + name])
    else return False
    return True
