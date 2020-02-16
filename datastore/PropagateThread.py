import struct
import time
import threading


class PropagateThread(threading.Thread):
    """
    The class for the sever to send the new data to other replica.
    """
    def __init__(self, datastore, vector_clock, replica_dic,
                 num_replica):
        threading.Thread.__init__(self)
        self.datastore = datastore
        self.vector_clock = vector_clock
        self.replica_dic = replica_dic
        self.num_replica = num_replica
        self.RECV_BUFFER = 4096
        self.RECV_MSG_LEN = 4

    def propagate_to_replica(self):
        pass

    def run(self):
        print("Start the propagation thread.")
        while True:
            time.sleep(5)
            self.propagate_to_replica()
