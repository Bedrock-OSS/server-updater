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

app.route('/status', methods=['GET'])(actions.status)
