import struct
import time
import threading


class VectorHandlerThread(threading.Thread):
    """
    1. The class for the sever to send the new data to other replica.
    2. Handles the received vector clock
    """
    def __init__(self, datastore, vector_clock, replica_dic,
                 num_replica, event):
        threading.Thread.__init__(self)
        self.datastore = datastore
        self.vector_clock = vector_clock
        self.replica_dic = replica_dic
        self.num_replica = num_replica
        self.RECV_BUFFER = 4096
        self.RECV_MSG_LEN = 4
        self.e = event

    def propagate_to_replica(self):
        pass

    def run(self):
        print("Start the propagation thread.")
        while True:
            event_is_set = self.e.wait(5)
            #time.sleep(5)
            # the value and vector are related, so we put all the
            # actions relted to vector_clock here
            if event_is_set:
                # when new message from other replica arrives
                # the server will put the message into VectorClock
                # check the received vector clock
                pass
            else:
                # the time is over, propagate to the replica
                self.propagate_to_replica()
