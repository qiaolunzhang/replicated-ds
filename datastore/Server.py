import socket
import threading
import struct
import logging
import time
from datastore.CausalDatastore import CausalDataStore
from datastore.ProcessThread import ProcessThread
from datastore.VectorClock import VectorClock

def thread_function(name, test_list):
    logging.info("Thread %s: starting", name)
    while True:
        time.sleep(2)
        print(test_list)
    logging.info("Thread %s: finishing", name)


class Server():
    def __init__(self, _datastore, _vector_clock, _num_replica, _e):
        self.datastore = _datastore
        # todo: this need to be changed, add a database interface
        self.datastore.locked_write("x", 1)
        self.LOCALHOST = "127.0.0.1"
        self.PORT = 8080
        self.local_replica_id = 0
        self.replica_dic = {}
        self.load_config()

        self.num_replica = _num_replica
        self.vector_clock = _vector_clock
        # the threading.Event object
        self.e = _e
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((self.LOCALHOST, self.PORT))
        print("Server started")
        print("Waiting for client request...")
        # test thread
        #x = threading.Thread(target=thread_function, args=(1, self.vector_clock))
        #x.start()
        while True:
            server_socket.listen(1)
            logging.info("A new conection")
            clientsock, clientAddress = server_socket.accept()
            newthread = ProcessThread(clientAddress, clientsock, self.datastore,
                                      self.num_replica, self.vector_clock)
            newthread.start()

    def load_config(self):
        try:
            with open('./config/server.conf') as f:
                for line in f:
                    if line[0] != '#':
                        line = line.split()
                        if line[0] == 'local_ip':
                            self.LOCALHOST = line[1]
                            self.PORT = int(line[2])
                            self.local_replica_id = int(line[3])
                        if line[0] == 'replica_ip':
                            replica_ip = line[1]
                            replica_port = int(line[2])
                            replica_id = int(line[3])
                            # todo: add available replica information to VectorClock
                            self.replica_dic[replica_id] = [replica_ip, replica_port]

        except Exception as e:
            print(Exception, ", ", e)



if __name__ == "__main__":
    format = '%(asctime)s: %(message)s'
    logging.basicConfig(format=format, level=logging.INFO,
                        datefmt="%H:%M:%S")
    #  You're free to mutate that object (if possible). However,
    #  integers are immutable. One workaround is to pass the integer
    #  in a container which can be mutated
    num_replica = 2
    vector_clock = VectorClock(num_replica, 0)
    num_replica = [1]
    datastore = CausalDataStore()
    e = threading.Event()
    server = Server(datastore, vector_clock, num_replica, e)

