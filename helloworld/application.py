#!flask/bin/python
import json
import core
from flask import Flask, request, Response, jsonify
import optparse

application = Flask(__name__)

@application.route('/signup', methods=['POST'])
def signup():
    credentials = request.get_json(force=True)
    return Response(json.dumps(core.signup(credentials)), mimetype='application/json', status=200)

@application.route('/login', methods=['POST'])
def login(): # Clients can use this route to check if login credentials are valid before trying to use them for anything else, but sessions are not persistent.
    credentials = request.get_json(force=True)
    return Response(json.dumps(core.authCheck(credentials)), mimetype='application/json', status=200)
    
@application.route('/startgame', methods=['POST'])
def startGame():
    credentials = request.get_json(force=True)
    return Response(json.dumps(core.authCheck(credentials) or core.startGame(credentials)), mimetype='application/json', status=200) # The "or" operation enforces middleware

@application.route('/getgame/<gameid>', methods=['GET'])
def getGame():
    credentials = request.get_json(force=True)
    return Response(json.dumps(core.authCheck(credentials)), mimetype='application/json', status=200)

@application.route('/movegame/<gameid>', methods=['POST'])
def moveGame(gameid):
    credentials = request.get_json(force=True)["credentials"] # This route should be called with a JSON containing credentials AND move
    move = request.get_json(force=True)["move"]
    return Response(json.dumps(core.authCheck(credentials) or core.gameCheck(credentials, gameid) or core.moveGame(move, gameid)), mimetype='application/json', status=200)

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
