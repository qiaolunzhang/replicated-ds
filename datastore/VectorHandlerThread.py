import struct
import time
import threading
from threading import Event
from datastore.CausalDatastore import CausalDataStore
from datastore.VectorClock import VectorClock


class VectorHandlerThread(threading.Thread):
    """
    1. The class for the sever to send the new data to other replica.
    2. Handles the received vector clock
    """

    def __init__(self, datastore: CausalDataStore, vector_clock: VectorClock, event: Event):
        threading.Thread.__init__(self)
        self.datastore = datastore
        self.vector_clock = vector_clock
        # self.replica_dic = replica_dic
        # self.num_replica = num_replica
        self.RECV_BUFFER = 4096
        self.RECV_MSG_LEN = 4
        self.e = event

    def propagate_to_replica(self):
        # get the newly changed value
        changed_value_dic = self.datastore.locked_propagate_to_replica()
        # get the vector clock and add it up with 1
        if bool(changed_value_dic):
            vector_clock_dic = self.vector_clock.locked_send_vector_clock()
            print("The vector clock dic to send is: ", vector_clock_dic)
            # todo: send to other server function
        else:
            print("The dict is empty")

    # todo: check the accept vector clock function
    def accept_vector_clocks(self):
        """
        # first check if there are new values to accept
        :return:
        """
        while True:
            value_to_update = self.vector_clock.get_vector_clock_message_to_accept()
            if value_to_update == "":
                break
            else:
                # change the value in VectorClock: x:3:y:4:z:5
                value_to_update_list = value_to_update.split(":")
                for i in range(len(value_to_update_list) // 2):
                    name_tmp = value_to_update_list[2 * i]
                    value_tmp = value_to_update_list[2 * i + 1]
                    self.datastore.locked_write(name_tmp, value_tmp)

    def run(self):
        print("Start the propagation thread.")
        while True:
            event_is_set = self.e.wait(5)
            # time.sleep(5)
            # the value and vector are related, so we put all the
            # actions relted to vector_clock here
            if event_is_set:
                # when new message from other replica arrives
                # the server will put the message into VectorClock
                # check the received vector clock
                # we need to clear it after process the  vector clock
                print("Now the event is set")
                self.e.clear()
                pass
            else:
                # the time is over, propagate to the replica
                print("Now propagate to replica")
                self.propagate_to_replica()
