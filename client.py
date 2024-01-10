from network import Network
import time

def run_stage(stage_name, prompt, stage_end_checker, n): # n is network
    # idk hwat the args should be yet
    new_input = True
    while True:
        if new_input:
            user_input = input(prompt)
            response = n.send(user_input)
            new_input = False
        end_stage, res = stage_end_checker(response)
        if not end_stage:
            response = n.send(None)
            print("printing response from stage: ", stage_name)
            print(response) # this is for debugging
        else:
            return res # stage res for using later

def name_stage_end_checker(response):
    return response[8] == 1, None

def repeat_stage_end_checker(response):
    return not (None in response), (response[1] and response[0])

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

    run_stage("name setup", "name: ", name_stage_end_checker, n)

    # run the game
    while run:
        if new_round:
            move = input("type move (r/p/s): ")
        else:
            move = None
        response = n.send(move)  # send the move to server, get game status back (if disconnect, receives None)
        # send something back to acknowledge the game status - this is prob the best way to fix the issue..


        if response is None:
            print("disconnected somehow")
            break
        prev_round = curr_round
        curr_round = response[5]
        print("prev round: ", prev_round)
        print("curr_round: ", curr_round)
        if not response[0]: # depends on whether the game status says it's changed before --> dependent on receiving that first game status :/
            # idea: some sort of handshake to acknowledge receipt??
            if not new_round:
                print("new roudn false, response[0] was False (no change reported)")
            else:
                print("new roudn true, response[0] was False (no change reported)")
            continue
        elif curr_round == prev_round: # this is really brittle
            if not new_round:
                continue
            print("waiting on the other guy")
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
            want_continue = run_stage("check new round", "new round? (y/n): ", repeat_stage_end_checker, n)
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
