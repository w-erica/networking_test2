# second version of client
# only ever plays r hahaha

from network import Network
import numpy as np
import time

rps = ['r', 'p', 's']
def main():
    run = True
    n = Network()
    curr_round = 0
    prev_round = 0
    move = None
    new_round = True
    new_name = True
    while True:
        if new_name:
            name = "r bot"
            response = n.send(name)
            new_name = False
        if response[8] == 0:
            response = n.send(None)
        elif response[8] == 1:
            break
    while run:
        if new_round:
            moveidx = np.random.randint(3)
            move = rps[moveidx]
        else:
            move = None
        response = n.send(move)  # send the move to server, get game status back (should never receive None)
        prev_round = curr_round
        curr_round = response[5]
        if not response[0]:
            continue
        elif curr_round == prev_round:
            if not new_round:
                continue
            print("waiting on the other guy")
            new_round = False
        elif response[6]:
            print("game over!")
            print("final scores:")
            print("you: ", response[3])
            print("other guy: ", response[4])
            if response[7]:
                print("you won!")
            else:
                print("you lost!")
            break
        else:
            print("round ended, moves were:")
            print("you: ", response[1])
            print("the other guy: ", response[2])
            print("=scores=")
            print("you: ", response[3])
            print("the other guy: ", response[4])
            print("==new round==")
            new_round = True

if __name__ == "__main__":
    main()
