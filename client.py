from typing import Callable

from network import Network
import time
import argparse
import socket
import numpy as np

rps = ['r', 'p', 's']
user_input = True
random_input = False
algo_input = False # some algorithm i will write that i think works ok


# handlers for each stage - NO WHILE LOOPS HERE. TAKES ACTION BASED ON GAME STATUS - ASSUMES STATUS HAS CHANGED SINCE
# LAST ACTION TAKEN. PRINTS OUTPUT AND RETURNS THE NEXT ACTION TO TAKE (CAN BE NONE)
def stage0_handler(game_info: tuple):
    if debug:
        print("DEBUG: ", "game info received: ", game_info)
    action = None
    if game_info[6]:
        print("trick ended, moves were:")
        print(game_info[9], "(you): ", game_info[1])
        print(game_info[10], "(other guy): ", game_info[2])
        print("ending the round")
        if game_info[7]:
            print("you won!")
        else:
            print("you lost!")
    elif game_info[12]:  # if both have gone
        if game_info[5] > 0:
            print("trick ended, moves were:")
            print(game_info[9], "(you): ", game_info[1])
            print(game_info[10], "(other guy): ", game_info[2])
            print("=scores=")
            print(game_info[9], "(you): ", game_info[3])
            print(game_info[10], "(other guy): ", game_info[4])
            print("==new trick==")
        if user_input:
            action = input("stage 0 input (r/p/s): ")
            while action not in rps:
                print("Move must be one of: r/p/s")
                action = input("stage 0 input (r/p/s): ")
        if random_input:
            action = rps[np.random.randint(3)]
    if not game_info[12]:  # if both have not gone
        print("waiting on the other guy")
    return action


def name_stage_handler(game_info: tuple):
    if debug:
        print("DEBUG: ", "game info received: ", game_info)
    action = None
    if game_info[0]:  # if received from the current guy yet
        if debug:
            print("DEBUG: waiting on the other guy's name")
        return None
    else:  # not received from the current guy
        if user_input:
            action = input("type name: ")
        elif random_input:
            action = "random boss"
        return action


def another_round_handler(game_info: tuple):
    action = None
    if game_info[1] is not None:
        if not game_info[1]:
            print("Opponent does not want another round!")
            return "DISCONNECT"
    if game_info[0] is None:
        if user_input:
            action = input("Another round? (y/n): ")
            while action not in ['y', 'n']:
                print("Please indicate y or n")
                action = input("Another round? (y/n): ")
        else:
            action = "y"
        return action


# MAIN CLIENT THING
def main():
    # set up game status variables
    local_status = None  # local status of the game

    # set up network
    n = Network()  # set up network

    # print init message
    init_message = n.init_message
    print(init_message)
    if init_message is None:
        print("There is an issue with connecting! Ending now.")
        return

    game_status = n.send(None)
    while True:
        action = None
        try:
            if local_status != game_status:
                local_status = game_status
                if debug:
                    print("Both connection: ", game_status[2])
                if game_status is None:
                    if debug:
                        print("DEBUG: disconnecting client side - None game status received")
                    break
                elif game_status[0] == 0:
                    action = stage0_handler(game_status[1])  # run round normally
                elif game_status[0] == 1:
                    action = name_stage_handler(game_status[1])  # setup name
                elif game_status[0] == -1:
                    print("Waiting for other players to connect")  # waiting for other players
                elif game_status[0] == 2:
                    action = another_round_handler(game_status[1])  # check if want to go another round
                elif not game_status[2]:  # means someone's disconnected
                    print("Someone else disconnected! Disconnecting here too.")
                    n.send("DISCONNECT")
                    break
                game_status = n.send(action)
                if action == "DISCONNECT":
                    print("ending game")
                    break
            else:
                game_status = n.send(None)
                continue
        except Exception as e:
            str(e)
            break
    n.close()

def dummy():
    print("hello world!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Client for rock paper scissors.')
    # parser.add_argument('') # add arguments for flags for client
    parser.add_argument('--dummy', dest='main_func', action='store_const',  # 2 dashes is for long flag
                        const=dummy, default=main,
                        help='set client (default: interact with a human)')
    parser.add_argument('--debug', dest='debug_flag', action=argparse.BooleanOptionalAction,
                        help='print debugging output')
    parser.add_argument('--random', dest='random_flag', action=argparse.BooleanOptionalAction,
                        help='automatically choose randomly r,p, or s')
    parser.add_argument('--algo', dest='algo_flag', action=argparse.BooleanOptionalAction,
                        help='run algo erica wrote :)')
    args = parser.parse_args()

    debug = args.debug_flag  # whether to print the debugging related messages or not

    # set up bools for behavior from flags
    random_input = args.random_flag
    algo_input = (not random_input) and args.algo_flag
    user_input = (not random_input) and (not algo_input)

    print(debug)
    args.main_func()
