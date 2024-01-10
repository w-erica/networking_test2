# based off techwithtim's online game tutorial

import socket
from _thread import *
import sys
from player import Player
import pickle
from rps import *

server = "192.168.0.208" #"127.0.0.1" #   # "192.168.86.38"
port = 5555

# set up socket and connection
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    s.bind((server, port))
except socket.error as e: # i think this is sometimes not working because sometimes the connection doesn't take
    str(e)

s.listen(4)  # 4 connections max, currently trying 2
print("Waiting for a connection, Server Started")

# new Game Wrapper object
games = GameWrapper()
print("started game initialization")

def send_game_status(conn, playeridx):
    game_status = games.game.getGameStatusForPlayer(playeridx)
    conn.send(pickle.dumps(game_status))  # send entire game status regardless

def name_handler(data, conn, playeridx):
    print("received name from player ", playeridx, ": ", data)
    games.game.updatePlayer(data, playeridx)
    send_game_status(conn, playeridx)
    return True

def name_end_checker(conn, playeridx):
    game_status = games.game.getGameStatusForPlayer(playeridx)
    conn.send(pickle.dumps(game_status))  # send entire game status regardless
    toend = (game_status[9]) is not None and (game_status[10] is not None) # whether to end the stage or not
    res = game_status
    done_stage = 0
    return toend, res, done_stage

def send_wrapper_status(conn, playeridx):
    wrapper_status = games.getWrapperStatusForPlayer(playeridx)
    conn.send(pickle.dumps(wrapper_status))

def get_agreement(data, conn, playeridx):
    print("player: ", playeridx, " agreement: ", data)
    # the following should be in the game wrapper lol.
    if data == 'y':
        games.agree[playeridx] = True
    else:
        games.agree[playeridx] = False
    wrapper_status = games.getWrapperStatusForPlayer(playeridx)
    conn.send(pickle.dumps(wrapper_status))
    return True

# loops and waits for client's response, executes something based on the response if present
def loop_n_wait(conn, nodata_handler, else_handler, playeridx):
    while True:
        try:
            data = pickle.loads(conn.recv(2048))
            if not data:
                nodata_handler(conn, playeridx)
            else:
                res = else_handler(data, conn, playeridx)
                if res:
                    break
        except socket.error as e:  # don't know what to use other than bare except here..
            str(e)
            break
    return

# this threaded client feels weird to have like. here. but i think it has to be here
def threaded_client(conn, playeridx):  # playeridx is the index in player ids
    # stage 0 - get player name set up
    init_message = "Connected to server, your player index: " + str(playeridx)
    conn.send(pickle.dumps(init_message))
    print("sent init message: ", init_message)
    loop_n_wait(conn, send_game_status, name_handler, playeridx)
    print("setup finished for player ", playeridx)

    # todo: stage 0.1 - set the desired until (figure out how to get the client info from each)

    # stage 1
    while True:
        try:
            data = pickle.loads(conn.recv(2048))
            if not data:
                pass  # keep looping if there is no data received
            elif data == "DISCONNECT":
                print("disconnect received from player idx: ", playeridx)
                break
            else:
                print("Received Move: ", data)
                games.game.updateGame(playeridx, data)  # perform move
                print("updated game state", playeridx)
            game_status = games.game.getGameStatusForPlayer(playeridx)
            conn.send(pickle.dumps(game_status))  # send entire game status regardless
            if game_status[6]:
                print("game is over!")
                loop_n_wait(conn, send_wrapper_status, get_agreement, playeridx)
                wrapper_status = games.getWrapperStatusForPlayer(playeridx)
                while None in wrapper_status:
                    wrapper_status = games.getWrapperStatusForPlayer(playeridx)
                    conn.send(pickle.dumps(wrapper_status))
                    print("wrapper status: ", wrapper_status)
                if False in wrapper_status:
                    print("ending games")
                    break
                else:
                    print("starting new game ", playeridx)
                    games.setNewGame()
                    games.agree = [None, None]
        except socket.error as e:  # don't know what to use other than bare except here..??
            str(e)
            break
    print("No more connection")
    conn.close()


# accepting connections
currentPlayerIdx = 0  # player id thing for accepting connections

while True:
    if currentPlayerIdx < 2:
        conn, addr = s.accept()  # i guess this is what connects a new network to a server
        print("Connected to: ", addr)
        print(currentPlayerIdx)
        # you start a new thread for every player
        start_new_thread(threaded_client, (conn, currentPlayerIdx))  # todo: figure out what start_new_thread does
        currentPlayerIdx += 1
    # else:
    #     print("another guy tried to connect, refused connection")

# how do you make it end once the threads wrap up..?
