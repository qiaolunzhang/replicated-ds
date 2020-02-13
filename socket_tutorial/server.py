import socket
import threading
import struct
class ClientThread(threading.Thread):
    def __init__(self, clientAddress, clientsocket):
        threading.Thread.__init__(self)
        self.clientAddress = clientAddress
        self.csocket = clientsocket
        print("New connection added: ", clientAddress)
    def run(self):
        print("Connection from: ", self.clientAddress)
        msg = ''

        data = self.csocket.recv(2048)
        msg = data.decode()
        print(msg)
        self.csocket.send(bytes(msg, 'UTF-8'))

        while True:
            # get the whole packet length
            # get the vector clock length (just to check if the vector is the same length
            # value_length = packet_length - packet_length_header - vector_clock_length_header - vector_clock_length
            # get the value
            print("started")
            tot_len = 0
            while tot_len < 4:
                key_length_pack = self.csocket.recv(4)
                tot_len = tot_len + len(key_length_pack)

            key_length = struct.unpack('>I', key_length_pack)[0]
            print(key_length)
            tot_len = 0
            while tot_len < 4:
                value_length_apck = self.csocket.recv(4)
                tot_len = tot_len + len(value_length_apck)
            value_length = struct.unpack('>I', value_length_apck)[0]
            tot_len = 0
            while tot_len < key_length:
                key = self.csocket.recv(key_length)
                tot_len = tot_len + len(key)
            tot_len = 0
            while tot_len < value_length:
                value = self.csocket.recv(value_length)
                tot_len = tot_len + len(value)
            print("key is: ", key)
            print("value is: ", value)

            data = self.csocket.recv(2048)
            msg = data.decode()
            if msg == 'bye':
                break
            print("from client", msg)
            data_store.append((msg))
            print(data_store)
        self.csocket.send(bytes(msg, 'UTF-8'))
        print("Client at ", self.clientAddress, " disconnected...")

LOCALHOST = "127.0.0.1"
PORT = 8080
data_store = ["original"]
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((LOCALHOST, PORT))
print("Server started")
print("Waiting for client request...")
while True:
    server.listen(1)
    clientsock, clientAddress = server.accept()
    newthread = ClientThread(clientAddress, clientsock)
    newthread.start()