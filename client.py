from typing import Callable

from network import Network
import time
import argparse
import socket

rps = ['r', 'p', 's']


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
        action = "DISCONNECT"
    elif game_info[12]:  # if both have gone
        if game_info[5] > 0:
            print("trick ended, moves were:")
            print(game_info[9], "(you): ", game_info[1])
            print(game_info[10], "(other guy): ", game_info[2])
            print("=scores=")
            print(game_info[9], "(you): ", game_info[3])
            print(game_info[10], "(other guy): ", game_info[4])
            print("==new trick==")
        action = input("stage 0 input (r/p/s): ")
        while action not in rps:
            print("Move must be one of: r/p/s")
            action = input("stage 0 input (r/p/s): ")
    if not game_info[12]:  # if both have not gone
        print("waiting on the other guy")
    return action


def name_stage_handler(game_info: tuple):
    if debug:
        print("DEBUG: ", "game info received: ", game_info)
    action = None
    if game_info[0]: # if received from the current guy yet
        if debug:
            print("DEBUG: waiting on the other guy's name")
        return None
    else: # not received from the current guy
        action = input("type name: ")
        return action



def main():
    # set up game status variables
    local_status = None  # local status of the game

    # set up network
    n = Network()  # set up network

    # print init message
    init_message = n.init_message
    print(init_message)
    if init_message is None:
        print("there is an issue with connecting! ending now.")
        return

    game_status = n.send(None)
    while True:
        action = None
        try:
            if local_status != game_status:
                local_status = game_status
                if game_status is None:
                    print("disconnecting client side - None game status received")
                    break
                elif game_status[0] == 0:
                    action = stage0_handler(game_status[1]) # some action to take if the game status is some typa way. NO LOOPS PLEASE
                elif game_status[0] == 1:
                    action = name_stage_handler(game_status[1])
                elif game_status[0] == -1:
                    print("Waiting for other players to connect")
                game_status = n.send(action)
                if action == "DISCONNECT":
                    print("ending game!")
                    break
            else:
                game_status = n.send(None)
                continue
        except Exception as e:
            str(e)
            break

# def name_stage_end_checker(response: tuple) -> tuple:
#     ''' :returns: whether to end the name stage. '''
#     if response is None:
#         return False, False
#     return response[8] == 1, True # 2nd return val isn't actually used at all
#
#
# def run_stage(stage_name: str, prompt: str, stage_end_checker: Callable[[tuple], tuple[bool, bool]], n: Network) -> bool:
#     """Help run a stage of the game.
#     :param stage_name: name of the stage (for internal use)
#     :param prompt: thing to ask the user for
#     :param stage_end_checker: function that takes the response (from the server) as input and returns (whether the stage is done,
#         some relevant information about what happened in the stage (for use after the stage is done))
#     :param n: network (used to send information)
#     :returns: boolean (?) relevant to what to do after the stage
#     """
#     response = None
#     new_input = True # whether to ask for a new input or not
#     while True:
#         if new_input:
#             user_input = input(prompt)
#             response = n.send(user_input)
#             new_input = False
#         end_stage, res = stage_end_checker(response)
#         if not end_stage:
#             response = n.send(None)
#             print("printing response from stage: ", stage_name) # for debugging
#             print(response)  # for debugging
#         else:
#             return res  # stage res for using later
#
#
# def repeat_stage_end_checker(response: tuple) -> tuple:
#     ''' :returns: whether to end the "new game?" stage, and also whether there will be new game or not. '''
#     if response is None:
#         return False, False
#     return not (None in response), (response[1] and response[0])
#
#
# def main():
#     n = Network() # set up network
#     curr_round = 0
#     prev_round = 0 # todo: not sure why this is the wrong scope
#     move = None # todo: also not sure about this one
#     response = None #todo: also this one lol
#     new_round = True
#
#     # print init message
#     init_message = n.init_message
#     print(init_message)
#
#     run_stage("name setup", "name: ", name_stage_end_checker, n)
#
#     # run the game
#     while True:
#         if new_round:
#             move = input("type move (r/p/s): ")
#             while move not in rps:
#                 print("input must be r, p, or s")
#                 move = input("type move (r/p/s): ")
#         else:
#             move = None
#         response = n.send((move, False))  # send the move to server, get game status back (if disconnect, receives None)
#         # todo: send something back to acknowledge the game status?? - this is prob the best way to fix the issue..
#         if response is None:
#             print("Disconnected from server.")
#             break
#         prev_round = curr_round
#         curr_round = response[5]
#         # print("prev round: ", prev_round) # for debugging
#         # print("curr_round: ", curr_round) # for debugging
#         if not response[0]:
#             continue
#         elif curr_round == prev_round:
#             if not new_round:
#                 continue
#             print("Waiting on other player")
#             n.send((None, True))
#             new_round = False
#         elif response[6]:
#             print("round ended, moves were:")
#             print(response[9], "(you): ", response[1])
#             print(response[10], "(other guy): ", response[2])
#             print("game over!")
#             print("final scores:")
#             print(response[9], "(you): ", response[3])
#             print(response[10], "(other guy): ", response[4])
#             if response[7]:
#                 print("you won!")
#             else:
#                 print("you lost!")
#             want_continue = run_stage("check new round", "new round? (y/n): ", repeat_stage_end_checker, n)
#             if want_continue:
#                 print("Starting new game!")
#                 curr_round = 0
#                 prev_round = 0
#                 move = None
#                 new_round = True
#                 response = None
#             else:
#                 print("No More Rock Paper Scissors.")
#                 break
#         else:
#             print("round ended, moves were:")
#             print(response[9], "(you): ", response[1])
#             print(response[10], "(other guy): ", response[2])
#             print("=scores=")
#             print(response[9], "(you): ", response[3])
#             print(response[10], "(other guy): ", response[4])
#             print("==new round==")
#             n.send((None, True))
#             new_round = True


def dummy():
    print("hello world!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Client for rock paper scissors.')
    #parser.add_argument('') # add arguments for flags for client
    parser.add_argument('--dummy', dest='main_func', action='store_const', # prob doesn't have to be 2 dashes but w/e
                        const=dummy, default=main,
                        help='set client (default: interact with a human)')
    parser.add_argument('--debug', dest='debug_flag', action=argparse.BooleanOptionalAction)
    args = parser.parse_args()
    debug = args.debug_flag # whether to print the debugging related messages or not
    print(debug)
    args.main_func()
    # main()
