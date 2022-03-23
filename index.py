from flask import Flask, request
# import the deploy file from the actions folder
from actions.common import *
import actions.deploy
import actions.query_status
import actions.set_status
import actions.create
import actions.delete
import actions.list

app = Flask(__name__)

@app.before_request
def check_creds():
    if(request.form["secret"] == config["secret"]):
        return None
    return "Invalid request", 400

app.route('/deploy', methods=['POST'])(actions.deploy.deploy)

app.route('/status', methods=['POST'])(actions.query_status.query_status)

app.route('/set_status', methods=['POST'])(actions.set_status.set_status)

app.route('/create', methods=['POST'])(actions.create.create)

app.route('/delete', methods=['POST'])(actions.delete.delete)

app.route('/list', methods=['POST'])(actions.list.list)

app.route('/restart', methods=['POST'])(actions.restart.restart)