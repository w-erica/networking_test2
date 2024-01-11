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
games = GameWrapper()
print("Started game initialization")

def send_game_status(conn, playeridx):
    game_status = games.game.get_game_status_for_player(playeridx)
    conn.send(pickle.dumps(game_status))  # send entire game status regardless

def name_handler(data, conn, playeridx):
    print("received name from player ", playeridx, ": ", data)
    games.game.update_player_name(data, playeridx)
    send_game_status(conn, playeridx)
    return True

def name_end_checker(conn, playeridx):
    game_status = games.game.get_game_status_for_player(playeridx)
    conn.send(pickle.dumps(game_status))  # send entire game status regardless
    toend = (game_status[9]) is not None and (game_status[10] is not None) # whether to end the stage or not
    res = game_status
    done_stage = 0
    return toend, res, done_stage

def send_wrapper_status(conn, playeridx):
    wrapper_status = games.get_wrapper_status_for_player(playeridx)
    conn.send(pickle.dumps(wrapper_status))

def get_agreement(data, conn, playeridx):
    print("player: ", playeridx, " agreement: ", data)
    # the following should be in the game wrapper lol.
    if data == 'y':
        games.agree[playeridx] = True
    else:
        games.agree[playeridx] = False
    wrapper_status = games.get_wrapper_status_for_player(playeridx)
    conn.send(pickle.dumps(wrapper_status))
    return True

# loops and waits for client's response, executes something based on the response if present
def loop_n_wait(conn: socket.socket, nodata_handler: Callable[[socket.socket, int], None],
                else_handler: Callable[[str, socket.socket, int], bool], p_idx: int) -> None:
    """ Wait for client response and once it arrives, execute something based on the response
    :param conn: socket for this player's client
    :param nodata_handler: function to run if no data is available
    :param else_handler: function to run once data is available, takes the data
        (may or may not be string but idk now to change it) as parameter, returns whether to stop looping or not
    :param p_idx: index for this player
    """
    while True:
        try:
            data = pickle.loads(conn.recv(2048))
            if not data:
                nodata_handler(conn, p_idx)
            else:
                res = else_handler(data, conn, p_idx)
                if res:
                    break
        except socket.error as e:
            str(e)
            break
    return


# this threaded client feels weird to have like. here. but i think it has to be here
def threaded_client(client_conn: socket.socket, player_idx: int) -> None:  # playeridx is the index in player ids
    """ Play game. 
    :param client_conn: connection
    :param player_idx: index for this player"""
    # stage 0 - get player name set up
    init_message = "Connected to server, your player index: " + str(player_idx)
    client_conn.send(pickle.dumps(init_message))
    print("sent init message: ", init_message) # for debugging?
    loop_n_wait(client_conn, send_game_status, name_handler, player_idx)
    print("setup finished for player ", player_idx) # for debugging? or maybe to keep

    # todo: stage 0.1 - set the desired until (value until which the game is played)
    # (figure out how to get the client info from each)

    # stage 1 - actual game
    while True:
        try:
            data = pickle.loads(client_conn.recv(2048))
            print("received from ", player_idx, ": ", data)
            if not data:
                pass  # keep looping if there is no data received
            elif data == "DISCONNECT":
                print("disconnect received from player idx: ", player_idx)
                break
            elif data[1]: # make this whether the player has been updated or not. should be separate from the move.
                games.game.mark_updated(player_idx)
            elif data[0]:
                print("Received Move: ", data[0])
                games.game.update_game(player_idx, data[0])  # perform move
                print("updated game state", player_idx)
            game_status = games.game.get_game_status_for_player(player_idx)
            client_conn.send(pickle.dumps(game_status))  # send entire game status regardless
            if game_status[6]:
                print("game is over!")
                # get whether player wants to continue with another round or not - i wanted to make this a separate
                # modular function but got confused
                loop_n_wait(client_conn, send_wrapper_status, get_agreement, player_idx)
                wrapper_status = games.get_wrapper_status_for_player(player_idx)
                print("wrapper status: ", wrapper_status)
                while None in wrapper_status:
                    wrapper_status = games.get_wrapper_status_for_player(player_idx)
                    client_conn.send(pickle.dumps(wrapper_status))
                if False in wrapper_status:
                    print("ending games")
                    break
                else:
                    print("starting new game ", player_idx)
                    games.set_new_game()
                    games.agree = [None, None]
        except socket.error as exception:
            str(exception)
            break
    print("No more connection")
    client_conn.close()


# accepting connections
curr_p_idx = 0  # player id thing for accepting connections

while True:
    if curr_p_idx < 2:
        conn, addr = s.accept()  # i guess this is what connects a new network to a server
        print(type(conn))
        print("Connected to: ", addr)
        print(curr_p_idx)
        # you start a new thread for every player
        start_new_thread(threaded_client, (conn, curr_p_idx))  # todo: figure out what start_new_thread does
        curr_p_idx += 1
    # else:
    #     print("another guy tried to connect, refused connection")

# how do you make it end once the threads wrap up..?
