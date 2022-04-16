import json
from flask import Flask, Response
import optparse
import numpy as np

BOARD_WIDTH = 7
BOARD_HEIGHT = 6
users = {} # username : password
games = {} # gameid : {status: ******, board: [******], turn: ******, players: [******, ******]}

# Adds user credentials to "users"
def signup(credentials):
    if (len(credentials["username"]) < 3 or len(credentials["username"]) > 10 or len(credentials["password"]) < 3 or len(credentials["password"]) > 10):
        return {'output': 'BAD SIGNUP | CREDENTIAL SPECIFICATIONS NOT MET'}
    if (credentials["username"] in users):
        return {'output': 'BAD SIGNUP | USER ALREADY EXISTS'}
    users[credentials["username"]] = credentials["password"]
    print(credentials["username"] + " SIGNED UP\n")
    return

# MIDDLEWARE | Checks if user has proper credentials
def authCheck(credentials): 
    if ((credentials["username"] in users) and users[credentials["username"]] == credentials["password"]):
        return
    return {'output': 'BAD LOGIN'}

# MIDDLEWARE | Checks if user is in turn
def gameCheck(credentials, gameid):
    authres = authCheck(credentials)
    if (authres):
        return authres
    if (games[gameid]["players"][games[gameid]["turn"] - 1] == credentials["username"]):
        return
    return {'output': 'NOT IN TURN'}

def startGame(credentials):
    print(credentials)
    for gameid in games: # Checks if a queueing game exists
        if (games[gameid]["status"] == "QUEUEING"):
            games[gameid]["status"] = "STARTED"
            games[gameid]["players"][1] = credentials["username"]
            return {"gameid" : gameid}
    # Creates new game if none queueing
    gameid = credentials["username"]
    print(gameid)
    if (gameid in games): # Ensures gameid uniqueness
        return {'output': 'BAD GAME'}
    games[gameid] = {"status": "QUEUEING", "board": np.zeros([BOARD_WIDTH, BOARD_HEIGHT], dtype = int), "turn": 1, "players": [credentials["username"], ""]}
    print(games)
    return {"gameid": gameid}

def endCheck(board):
    # ...
    return False

def moveGame(move, gameid):
    column = int(move) % BOARD_WIDTH # Modulus by the board's width just in case
    board = games[gameid]["board"] # Grabs board data and updates it to reflect move
    if (board[column][0] != 0): # Makes sure the column isn't already full
        return
    y = 0
    while (y < BOARD_HEIGHT):
        if ((y == (BOARD_HEIGHT - 1)) or (board[column][y + 1] != 0)):
            board[column][y] = games[gameid]["turn"]
            break
        y += 1
    games[gameid]["board"] = board
    games[gameid]["turn"] = (games[gameid]["turn"] % 2) + 1 # Mathy way to switch turns
    # Checks if game has ended
    if endCheck(board):
        games[gameid]["status"] = "OVER"
        # ...
    print(games[gameid]["board"])
    return