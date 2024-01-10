import socket
import time
import pickle


class Network:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = "192.168.0.208"# "127.0.0.1" # #"192.168.86.38"  # to make it the same as the server
        self.port = 5555
        self.addr = (self.server, self.port)
        self.init_message = self.connect()  # first thing received from the server

    def connect(self):
        try:
            self.client.connect(self.addr)  # networking thing to connect to the server
            time.sleep(1)
            received = pickle.loads(self.client.recv(2048))  # receive initial thing from the server (player name rn)
            return received
        except socket.error as e:
            str(e)

    def send(self, data):
        try:
            self.client.send(pickle.dumps(data))
            reply = self.client.recv(2048) # can never be None otherwise it'll disconnect
            # just return none
            if reply is None:
                print("reply is none for some reason!")
                return None
            else:
                reply = pickle.loads(reply)
                return reply
        except EOFError:
            return None
        except socket.error as e:
            print(e)

# dunno if should be using this one - no need, right?
    def receive(self):
        try:
            print("receiving?")
            reply = self.client.recv(2048)
            reply = pickle.loads(reply)
            return reply
        except socket.error as e:
            print(e)
