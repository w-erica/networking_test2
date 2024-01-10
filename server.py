# based off techwithtim's online game tutorial

import socket
from _thread import *
import sys
from player import Player
import pickle
from rps import Game

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

# new Game object
thisGame = Game()
print("started game initialization")

def send_game_status(conn, playeridx):
    game_status = thisGame.getGameStatusForPlayer(playeridx)
    conn.send(pickle.dumps(game_status))  # send entire game status regardless

def name_handler(data, conn, playeridx):
    print("received name from player ", playeridx, ": ", data)
    thisGame.updatePlayer(data, playeridx)
    send_game_status(conn, playeridx)
    return True


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

    thisGame.until = 3
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
                thisGame.updateGame(playeridx, data)  # perform move
                print("updated game state", playeridx)
            game_status = thisGame.getGameStatusForPlayer(playeridx)
            conn.send(pickle.dumps(game_status))  # send entire game status regardless
            if game_status[6]:
                print("game is over!")
                break
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
