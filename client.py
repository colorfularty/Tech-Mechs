import socket, pickle
from constants import *

class Client(object):
    # the client that sends and receive data across the server

    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect(('127.0.0.1', PORT))

    def sendString(self, s):
        self.sock.send(s.encode())

    def receiveString(self):
        return self.sock.recv(1024).decode()

    def sendTuple(self, data):
        safeData = pickle.dumps(data)
        self.sock.send(safeData)

    def receiveTuple(self):
        safeData = self.sock.recv(1024)
        data = pickle.loads(safeData)
        return data
