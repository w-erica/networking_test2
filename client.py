from network import Network

def main():
    run = True
    n = Network()
    curr_round = 0
    prev_round = 0
    move = None
    new_round = True
    new_name = True
    response = None

    # print init message
    init_message = n.init_message
    print(init_message)

    # name setup
    while True:
        if new_name:
            name = input("name: ")
            response = n.send(name)
            new_name = False
        if response[8] == 0:
            response = n.send(None)
            print(response)
        elif response[8] == 1:
            break

    # run the game
    while run:
        if new_round:
            move = input("type move (r/p/s): ")
        else:
            move = None
        response = n.send(move)  # send the move to server, get game status back (if disconnect, receives None - todo: handle this)
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
            print(response[9], "(you): ", response[3])
            print(response[10], "(other guy): ", response[4])
            if response[7]:
                print("you won!")
            else:
                print("you lost!")
            new_continue = True
            want_continue = -1
            while True:
                if new_continue:
                    want_continue = input("new round? (y/n): ") # though anything but 'y' is considered n haha
                    response = n.send(want_continue)
                    if want_continue != 'y':
                        break
                    new_continue = False
                if None in response:
                    response = n.send(None)
                    print("received response")
                    print(response)
                elif not response[1]:
                    want_continue = 'n'
                    break
                else:
                    want_continue = 'y'
                    break
            if want_continue != 'y':
                print("No More Rock Paper Scissors.")
                break
            else:
                print("Starting new game!")
                curr_round = 0
                prev_round = 0
                move = None
                new_round = True
                response = None
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
