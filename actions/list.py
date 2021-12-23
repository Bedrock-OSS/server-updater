import json
import os
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
                "status": get_status(item, 'bedrock-oss')
            })
    return json.dumps(items), 200
