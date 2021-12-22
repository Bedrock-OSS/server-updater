import json
import os
from common import get_process_config
def list():
    # Create a list of all items in the repos folder
    items = []
    for item in os.listdir('/home/ubuntu/oss/repos'):
        if os.path.isdir(os.path.join('/home/ubuntu/oss/repos', item)):
            items.append({
                "item": item,
                "config": get_process_config(item)
            })
    return json.dumps(items), 200
