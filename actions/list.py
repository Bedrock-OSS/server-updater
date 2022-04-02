import json
import os
from subprocess import check_output
from actions.common import get_process_config
from actions.query_status import get_status
def list():
    # Create a list of all items in the repos folder
    items = []
    for item in os.listdir('/home/ubuntu/oss/repos'):
        if os.path.isdir(os.path.join('/home/ubuntu/oss/repos', item)):
            items.append({
                "item": item,
                "config": get_process_config(item),
                "status": get_status(item, 'bedrock-oss'),
                "last-commit-time": check_output(["git", "show", "-s", "--format=%ct", "HEAD"], cwd='/home/ubuntu/oss/repos/' + item).decode('utf-8').strip(),
                "last-commit-hash": check_output(["git", "rev-parse", "HEAD"], cwd='/home/ubuntu/oss/repos/' + item).decode('utf-8').strip()
            })
    items.append({
        "item": "server-updater",
        "last-commit-time": check_output(["git", "show", "-s", "--format=%ct", "HEAD"], cwd='/home/ubuntu/oss').decode('utf-8').strip(),
        "last-commit-hash": check_output(["git", "rev-parse", "HEAD"], cwd='/home/ubuntu/oss').decode('utf-8').strip()
    })
    return json.dumps(items), 200
