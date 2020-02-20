import socket
import threading
import struct
import logging
import time
from datastore.CausalDatastore import CausalDataStore
from datastore.ProcessThread import ProcessThread
from datastore.VectorClock import VectorClock

class ControlThread(threading.Thread):
    def __init__(self, datastore: CausalDataStore, vector_clock: VectorClock):
        threading.Thread.__init__(self)
        self.datastore = datastore
        self.vector_clock = vector_clock

    def run(self):
        while True:
            command = input("Please type your command: ")
            if command == "show datastore":
                print(self.datastore.value_dic)
