import json
from flask import Flask, Response, jsonify
import optparse
from numpy import zeros

BOARD_WIDTH = 7
BOARD_HEIGHT = 6
users = {} # username : {password, gameid} 
games = {} # gameid : {status: ******, board: [******], turn: ******, players: [******, ******]}

# Adds user credentials to "users"

def badReq(msg = 'UNSPECIFIED', load = {}):
    data = {'ERR': msg}
    data.update(load)
    return Response(json.dumps(data), mimetype='application/json', status=400)

def goodReq(msg = 'UNSPECIFIED', load = {}):
    data = {'GTG': msg}
    data.update(load)
    return Response(json.dumps(data), mimetype='application/json', status=200)

# MIDDLEWARE
def signup(credentials):
    try:
        if (len(credentials["USERNAME"]) < 3 or len(credentials["USERNAME"]) > 10 or len(credentials["PASSWORD"]) < 3 or len(credentials["PASSWORD"]) > 10):
            return badReq('BAD SIGNUP | CREDENTIAL SPECIFICATIONS NOT MET')
        if (credentials["USERNAME"] in users):
            return badReq('BAD SIGNUP | USER ALREADY EXISTS')
        users[credentials["USERNAME"]]= {'PASSWORD': credentials["PASSWORD"], 'GAMEID': None}
        print(credentials["USERNAME"] + " SIGNED UP\n")
        return
    except:
        return badReq("BAD SIGNUP | INTERNAL ERROR")

# MIDDLEWARE | Checks if user has proper credentials
def authCheck(credentials):
    try:
        if ((credentials["USERNAME"] in users) and users[credentials["USERNAME"]]['PASSWORD'] == credentials["PASSWORD"]):
            return
        return badReq('BAD LOGIN | INVALID USERNAME/PASSWORD COMBINATION')
    except:
        return badReq('BAD LOGIN | INTERNAL ERROR')

# MIDDLEWARE | Checks if user is in turn
def gameCheck(credentials, gameid):
    try:
        authres = authCheck(credentials)
        if (authres):
            return authres
        if (games[gameid]["PLAYERS"][games[gameid]["TURN"]] == credentials["USERNAME"]):
            return
        return badReq('BAD MOVE | NOT IN TURN')
    except:
        return badReq('BAD MOVE | INTERNAL ERROR')

def startGame(credentials):
    try:
        print("CREDENTIALS ARE:")
        print(credentials)
        if (users[credentials['USERNAME']]['GAMEID'] != None):
            return badReq('BAD START | USER ALREADY IN GAME')
        for gameid in games: # Checks if a queueing game exists
            if (games[gameid]["STATUS"] == "QUEUEING"):
                games[gameid]["STATUS"] = "STARTED"
                games[gameid]["PLAYERS"][1] = credentials["USERNAME"]
                users[credentials['USERNAME']]['GAMEID'] = gameid
                return goodReq("YOU JOINED " + gameid, load = {"GAMEID": gameid, "GAME": games[gameid]})
        # Creates new game if none queueing
        gameid = credentials["USERNAME"]
        users[credentials["USERNAME"]]['GAMEID'] = gameid
        games[gameid] = {"STATUS": "QUEUEING", "BOARD": zeros([BOARD_WIDTH, BOARD_HEIGHT], dtype = int).tolist(), "TURN": 0, "PLAYERS": [credentials["USERNAME"], ""]}
        return goodReq("YOU STARTED A NEW GAME", load = {"GAMEID": gameid, "GAME": games[gameid]})
    except:
        return badReq('BAD START | INTERNAL ERROR')

def getGame(gameid):
    try:
        if gameid in games:
            return goodReq(load = {"GAME": games[gameid]})
        return badReq('BAD GETGAME | GAMEID INVALID')
    except:
        return badReq('BAD GETGAME | INTERNAL ERROR')

def moveGame(move, gameid):
    try:
        if not(gameid in games):
            return badReq('BAD MOVE | GAMEID INVALID')
        column = int(move) % BOARD_WIDTH # Modulus by the board's width just in case
        board = games[gameid]["BOARD"] # Grabs board data and updates it to reflect move
        if (board[column][0] != 0): # Makes sure the column isn't already full
            return badReq("BAD MOVE | COLUMN IS FULL", load = {"GAME": games[gameid]})
        row = 0
        while (row < BOARD_HEIGHT):
            if ((row == (BOARD_HEIGHT - 1)) or (board[column][row + 1] != 0)):
                board[column][row] = games[gameid]["TURN"] + 1
                break
            row += 1
        games[gameid]["BOARD"] = board
        games[gameid]["TURN"] = (games[gameid]["TURN"] % 2 + 1) # Mathy way to switch turns
        # Checks if game has ended
        if endCheck(board, column, row):
            games[gameid]["STATUS"] = "OVER"
            response = goodReq("GAME OVER", load = {"GAME": games[gameid]})
            endGame(gameid)
            return response
        return goodReq("SUCCESFUL MOVE", load = {"GAME": games[gameid]})
    except:
        return badReq('BAD MOVE | INTERNAL ERROR')

    # By passing the location of the last move
    # instead of checking the whole board,
    # checking for end of game is 40x faster
def endCheck(board, column, row):
    try:
        marker = board[column][row]
        for i in range(-1, 2):
            for j in range(-1, 2):
                if (i != 0 or j != 0):
                    count = 1
                    x = column + i
                    y = row + j
                    while ((x < BOARD_WIDTH and y < BOARD_HEIGHT) and board[x][y] ==  marker):
                        count += 1
                        x += i
                        y += j
                        if (count == 4): # four in a row
                            return True
        return False
    except:
        return True

def endGame(gameid):
    try:
        del games[gameid]
        # log win for scoreboard
        return # result = winner's name or 'TIE'
    except:
        return