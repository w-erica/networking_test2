import socket
import time
import pickle

# Class for connecting client and server - derived in large part from techwithtim's online game tutorial

class Network:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = "192.168.86.46" #"192.168.0.208"# "127.0.0.1" # #"192.168.86.38"  # to make it the same as the server
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
            if reply is None:
                print("reply is none for some reason! this isn't good!") # for debugging
                return None
            else:
                reply = pickle.loads(reply)
                return reply
        except EOFError:
            return None
        except socket.error as e:
            print(e)

    def close(self):
        self.client.close()
        return

# not using this one at the moment - I'm just using None with the send function.
    def receive(self):
        try:
            print("receiving?") # for debugging
            reply = self.client.recv(2048)
            reply = pickle.loads(reply)
            return reply
        except socket.error as e:
            print(e)
