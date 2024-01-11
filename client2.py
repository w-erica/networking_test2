# second version of client
# is a "bot" that plays randomly (what is the definition of a bot anyways?)

# not currently working.

from network import Network
import numpy as np
from typing import Callable

rps = ['r', 'p', 's']

def run_stage(stage_name: str, bot_input: str, stage_end_checker: Callable[[tuple], tuple[bool, bool]], n: Network) -> bool:
    """Help run a stage of the game.
    :param stage_name: name of the stage (for internal use)
    :param prompt: thing to ask the user for
    :param stage_end_checker: function that takes the response (from the server) as input and returns (whether the stage is done,
        some relevant information about what happened in the stage (for use after the stage is done))
    :param n: network (used to send information)
    :returns: boolean (?) relevant to what to do after the stage
    """
    response = None
    new_input = True # whether to ask for a new input or not
    while True:
        if new_input:
            user_input = bot_input
            response = n.send(user_input)
            new_input = False
        end_stage, res = stage_end_checker(response)
        if not end_stage:
            response = n.send(None)
            if not response:
                continue
        else:
            return res  # stage res for using later


def name_stage_end_checker(response: tuple) -> tuple:
    ''' :returns: whether to end the name stage. '''
    return response[8] == 1, True # 2nd return val isn't actually used at all


def repeat_stage_end_checker(response: tuple) -> tuple:
    ''' :returns: whether to end the "new game?" stage, and also whether there will be new game or not. '''
    return not (None in response), (response[1] and response[0])


def main():
    n = Network() # set up network
    curr_round = 0
    prev_round = 0 # todo: not sure why this is the wrong scope
    move = None # todo: also not sure about this one
    response = None #todo: also this one lol
    new_round = True

    # print init message
    init_message = n.init_message
    print(init_message)

    run_stage("name setup", "random bot!", name_stage_end_checker, n)

    # run the game
    while True:
        if new_round:
            moveidx = np.random.randint(3)
            move = rps[moveidx]
        else:
            move = None
        response = n.send(move)  # send the move to server, get game status back (if disconnect, receives None)
        # todo: send something back to acknowledge the game status?? - this is prob the best way to fix the issue..

        if response is None:
            print("Disconnected from server.")
            break
        prev_round = curr_round
        curr_round = response[5]
        # print("prev round: ", prev_round) # for debugging
        # print("curr_round: ", curr_round) # for debugging
        if not response[0]:  # depends on whether the game status says it's changed before --> dependent on receiving that first game status :/
            # # for debugging:
            # if not new_round:
            #     print("new roudn false, response[0] was False (no change reported)")
            # else:
            #     print("new roudn true, response[0] was False (no change reported)")
            continue
        elif curr_round == prev_round:
            if not new_round:
                continue
            print("Waiting on other player")
            new_round = False
        elif response[6]:
            print("round ended, moves were:")
            print(response[9], "(you): ", response[1])
            print(response[10], "(other guy): ", response[2])
            print("game over!")
            print("final scores:")
            print(response[9], "(you): ", response[3])
            print(response[10], "(other guy): ", response[4])
            if response[7]:
                print("you won!")
            else:
                print("you lost!")
            want_continue = run_stage("check new round", 'y', repeat_stage_end_checker, n)
            if want_continue:
                print("Starting new game!")
                curr_round = 0
                prev_round = 0
                move = None
                new_round = True
                response = None
            else:
                print("No More Rock Paper Scissors.")
                break
        else:
            print("round ended, moves were:")
            print(response[9], "(you): ", response[1])
            print(response[10], "(other guy): ", response[2])
            print("=scores=")
            print(response[9], "(you): ", response[3])
            print(response[10], "(other guy): ", response[4])
            print("==new round==")
            new_round = True


if __name__ == "__main__":
    main()
