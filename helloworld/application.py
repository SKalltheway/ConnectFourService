#!flask/bin/python
import json
import helloworld.core as core
from flask import Flask, request, jsonify, Response
import optparse

application = Flask(__name__)

@application.route('/signup', methods=['POST'])
def signup():
    credentials = request.get_json(force=True)
    return core.signup(credentials) or core.goodReq('SUCCESSFUL SIGN UP')

@application.route('/login', methods=['POST'])
def login(): # Clients can use this route to check if login credentials are valid before trying to use them for anything else, but sessions are not persistent.
    credentials = request.get_json(force=True)
    return core.authCheck(credentials) or core.goodReq('SUCCESSFUL LOGIN')

@application.route('/startgame', methods=['POST'])
def startGame():
    credentials = request.get_json(force=True)
    return core.authCheck(credentials) or core.startGame(credentials)

@application.route('/getgame/<gameid>', methods=['GET'])
def getGame(gameid):
    credentials = request.get_json(force=True)
    return core.authCheck(credentials) or core.getGame(gameid)

@application.route('/movegame/<gameid>', methods=['POST'])
def moveGame(gameid): # This route should be called with a JSON containing credentials AND move
    data = request.get_json(force=True)
    credentials = data["CREDENTIALS"]
    move = data["MOVE"]
    return core.authCheck(credentials) or core.gameCheck(credentials, gameid) or core.moveGame(move, gameid)

if __name__ == '__main__':
    default_port = "80"
    default_host = "0.0.0.0"
    parser = optparse.OptionParser()
    parser.add_option("-H", "--host",
                      help=f"Hostname of Flask app {default_host}.",
                      default=default_host)

    parser.add_option("-P", "--port",
                      help=f"Port for Flask app {default_port}.",
                      default=default_port)

    parser.add_option("-d", "--debug",
                      action="store_true", dest="debug",
                      help=optparse.SUPPRESS_HELP)

    options, _ = parser.parse_args()

    application.run(
        debug=options.debug,
        host=options.host,
        port=int(options.port)
    )