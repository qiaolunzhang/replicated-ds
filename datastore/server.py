import socket
import threading
import struct
import logging
import time
from datastore.CausalDatastore import CausalDataStore
from datastore.ProcessThread import ProcessThread

def thread_function(name, test_list):
    logging.info("Thread %s: starting", name)
    while True:
        time.sleep(2)
        print(test_list)
    logging.info("Thread %s: finishing", name)


class Server():
    def __init__(self, _datastore, _vector_clock, _num_replica, e):
        self.datastore = _datastore
        self.datastore.locked_write("x", 1)
        self.LOCALHOST = "127.0.0.1"
        self.PORT = 8080
        self.num_replica = _num_replica
        self.vector_clock = _vector_clock
        # the threading.Event object
        self.e = e
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((self.LOCALHOST, self.PORT))
        print("Server started")
        print("Waiting for client request...")
        # test thread
        x = threading.Thread(target=thread_function, args=(1, self.vector_clock))
        x.start()
        while True:
            server.listen(1)
            clientsock, clientAddress = server.accept()
            newthread = ProcessThread(clientAddress, clientsock, self.datastore,
                                      self.num_replica, self.vector_clock)
            newthread.start()
            #time.sleep(20)
            #print(self.vector_clock)



if __name__ == "__main__":
    format = '%(asctime)s: %(message)s'
    logging.basicConfig(format=format, level=logging.INFO,
                        datefmt="%H:%M:%S")
    #  You're free to mutate that object (if possible). However,
    #  integers are immutable. One workaround is to pass the integer
    #  in a container which can be mutated
    vector_clock = [0]
    num_replica = [1]
    datastore = CausalDataStore()
    e = threading.Event()
    server = Server(datastore, vector_clock, num_replica, e)

