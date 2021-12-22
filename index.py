from flask import Flask, request
# import the deploy file from the actions folder
import actions
from actions.common import *

app = Flask(__name__)

@app.before_request
def check_creds():
    if(request.form["secret"] == config["secret"]):
        return None
    return "Invalid request", 500

app.route('/deploy', methods=['POST'])(actions.deploy)

app.route('/status', methods=['POST'])(actions.query_status)

app.route('/set_status', methods=['POST'])(actions.set_status)

app.route('/create', methods=['POST'])(actions.create)

app.route('/delete', methods=['POST'])(actions.delete)

app.route('/list', methods=['POST'])(actions.list)