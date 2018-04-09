import socket, pickle
from threading import Thread
from constants import PORT

class Server(object):
    # the server that sends and receives data across clients

    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind(('', PORT))
        while True:
            self.sock.listen(2)
            clients = [] # a list of client connections
            # get the client connections
            connection, clientAddress = self.sock.accept()
            clients.append(connection)
            connection.send("0".encode()) # the first one to connect is player num 0
            connection, clientAddress = self.sock.accept()
            clients.append(connection)
            connection.send("1".encode()) # the second one to connect is player num 1
            # start threads to listen to the clients
            Thread(target = self.listenToClient, args = (0,clients,)).start()
            Thread(target = self.listenToClient, args = (1,clients,)).start()

    def listenToClient(self, clientNum, clients):
        while True:
            # wait to receive data from the client
            data = clients[clientNum].recv(1024)
            try:
                if data.decode() == "Quit server":
                    #finalData = pickle.dumps((None, None, None, None))
                    #clients[not clientNum].send(finalData)
                    break
            except UnicodeDecodeError:
                pass
            # send the data to the other client
            clients[not clientNum].send(data)
