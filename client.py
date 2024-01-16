from typing import Callable

from network import Network
import time
import argparse
import socket
import numpy as np
import algos

# flags
user_input = True
random_input = False
algo_input = False
record_inputs = False
algo_num = -1

possible_algo_nums = [0, 1] # possible import from algos module
rps = ['r', 'p', 's']

# thing for if using algos
algo_wrapper = None


# handlers for each stage - NO WHILE LOOPS HERE. TAKES ACTION BASED ON GAME STATUS - ASSUMES STATUS HAS CHANGED SINCE
# LAST ACTION TAKEN. PRINTS OUTPUT AND RETURNS THE NEXT ACTION TO TAKE (CAN BE NONE)
def stage0_handler(game_info: tuple) -> str:
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
        if record_inputs:
            # some file i/o thing here
            pass
        if algo_input:
            algo_wrapper.update_moves(game_info[1], game_info[2])
    elif game_info[12]:  # if both have gone
        if game_info[5] > 0:
            print("trick ended, moves were:")
            print(game_info[9], "(you): ", game_info[1])
            print(game_info[10], "(other guy): ", game_info[2])
            print("=scores=")
            print(game_info[9], "(you): ", game_info[3])
            print(game_info[10], "(other guy): ", game_info[4])
            print("==new trick==")
            if record_inputs:
                # file i/o
                pass
            if algo_input:
                algo_wrapper.update_moves(game_info[1], game_info[2])
        # actions to take depending on game mode
        if user_input:
            action = input("stage 0 input (r/p/s): ")
            while action not in rps:
                print("Move must be one of: r/p/s")
                action = input("stage 0 input (r/p/s): ")
        elif random_input:
            action = rps[np.random.randint(3)]
        elif algo_input:
            action = algo_wrapper.get_move()
    if not game_info[12]:  # if both have not gone
        print("waiting on the other guy")
    return action


def name_stage_handler(game_info: tuple) -> str:
    if debug:
        print("DEBUG: ", "game info received: ", game_info)
    action = None
    if game_info[0]:  # if received from the current guy yet
        if debug:
            print("DEBUG: waiting on the other guy's name")
        return action
    else:  # not received from the current guy
        if user_input:
            action = input("type name: ")
        elif random_input:
            action = "random chooser"
        elif algo_input:
            action = "algo " + str(algo_num)
        return action


def another_round_handler(game_info: tuple) -> str:
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

    # ensure connection, print init message
    init_message = n.init_message
    if init_message is None:
        print("There is an issue with connecting! Ending now.")
        return
    print(init_message)

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
    # close file i/o if needed


def dummy():
    print("hello world!")


if __name__ == "__main__":
    # set up and parse arguments
    parser = argparse.ArgumentParser(description='Client for rock paper scissors.')
    parser.add_argument('--dummy', dest='main_func', action='store_const',  # 2 dashes is for long flag
                        const=dummy, default=main,
                        help='set client (default: interact with a human)')
    parser.add_argument('--debug', dest='debug_flag', action=argparse.BooleanOptionalAction,
                        help='print debugging output')
    parser.add_argument('--random', dest='random_flag', action=argparse.BooleanOptionalAction,
                        help='automatically choose randomly r,p, or s')
    parser.add_argument('--record', dest='record_flag', action=argparse.BooleanOptionalAction,
                        help='record inputs in a file!')
    parser.add_argument('-a', '--algo', dest='algo_num', help='run indicated algo', type=int)

    args = parser.parse_args()

    # set output depending on arguments
    debug = args.debug_flag  # whether to print the debugging related messages or not

    # set game mode depending on arguments
    random_input = args.random_flag
    algo_num = args.algo_num
    algo_input = (not random_input) and (algo_num in possible_algo_nums)

    # make it record inputs if using the algo i'm writing
    record_inputs = algo_input
    if not record_inputs:
        record_inputs = args.record_flag

    # option to update algo_num
    if algo_num and algo_num not in possible_algo_nums:
        print("Algo num input not valid (options are: ", possible_algo_nums, ")")
        while True:
            algo_num = input("New algo_num input (type QUIT to use user input instead): ")
            if algo_num == "QUIT":
                print("Using user input for this client!")
                break
            elif algo_num.isdigit() and int(algo_num) in possible_algo_nums:
                print("Using algo ", algo_num)
                algo_input = True
                break

    if algo_input:
        # initialize algowrapper for the client with the right algo number
        algo_wrapper = algos.AlgoWrapper(algo_num)

    if record_inputs:
        # write out time
        # write out somewhere (maybe at bottom) the two names
        # each move, write out: "my_move, their_move\n"
        # todo: initialize file i/o?? for recording inputs? is there a way to do the file i/o with knowing the opponent's name?
        pass

    user_input = (not random_input) and (not algo_input)

    if debug:
        print("algo input: ", algo_input)
        print("random input: ", random_input)
        print("algo num: ", algo_num)
        print("algo num in possible: ", algo_num in possible_algo_nums)
        print("not random: ", not random_input)

    args.main_func()
