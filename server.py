# based off techwithtim's online game tutorial

import socket
from _thread import *
import pickle
from typing import Callable

from rps import *

# setup according to the server and port
server = "192.168.0.208" #"127.0.0.1" #   # "192.168.86.38"
port = 5555

# setup connection
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    s.bind((server, port))
except socket.error as e: # todo: i think this is sometimes not working because sometimes the connection doesn't take but it just goes on
    str(e)
s.listen(2)  # 2 connections max
print("Waiting for a connection, Server Started")

# define new GameWrapper object
game = GameWrapper()
print("Started game initialization")


# this threaded client feels weird to have like. here. but i think it has to be here
def threaded_client(client_conn: socket.socket, player_idx: int) -> None:  # playeridx is the index in player ids
    """ Play game. 
    :param client_conn: connection
    :param player_idx: index for this player"""
    # send initial message
    init_message = "Connected to server, your player index: " + str(player_idx)

    client_conn.send(pickle.dumps(init_message))
    print("sent init message: ", init_message) # for debugging?

    game.update_connected(True, player_idx) # send that a certain player has connected

    # actual game stage
    while True:
        try:
            game_status = game.get_game_status_for_player(player_idx)
            action = pickle.loads(client_conn.recv(2048))  # this is the action from the player
            if action:
                print("received from ", player_idx, ": ", action)
            if not action:
                pass  # keep looping if there is no action received
            elif action == "DISCONNECT":
                print("disconnect received from player idx: ", player_idx)
                game.bothConnectedLater = False
                client_conn.send(pickle.dumps((-2, "DISCONNECTING")))
                break
            elif action:
                if game_status[0] == 0: # what to server side if the game status is 0 and an action has been received
                    print("Received Move: ", action)
                    game.round.update_round(action, player_idx)  # perform move
                    print("updated game state", player_idx)
                if game_status[0] == 1: # name section
                    print("Received Name: ", action)
                    game.update_player_name(action, player_idx)
                if game_status[0] == 2:
                    print("Received continue desire: ", action)
                    game.update_continue(action, player_idx)
                    if action == "n":
                        break
                game_status = game.get_game_status_for_player(player_idx)
            client_conn.send(pickle.dumps(game_status))  # send entire game status regardless
            if game_status[0] == 0 and game_status[1][6]:
                print("game (round) is over!")
                client_conn.send(pickle.dumps(game_status))  # send entire game status regardless
                game.stage = 2 # is this ok?
        except socket.error as exception:
            str(exception)
            break
        except EOFError as exception:
            str(exception)
            break
    print("No more connection")
    client_conn.close()

# accepting connections
curr_p_idx = 0  # player id thing for accepting connections

while True:
    if curr_p_idx < 2:
        conn, addr = s.accept()
        print(type(conn))
        print("Connected to: ", addr)
        print(curr_p_idx)
        # you start a new thread for every player
        start_new_thread(threaded_client, (conn, curr_p_idx))  # todo: figure out what start_new_thread does
        curr_p_idx += 1
    if not game.bothConnectedLater:
        break
