import struct
import time
import socket
import threading
from threading import Event
from datastore.CausalDatastore import CausalDataStore
from datastore.VectorClock import VectorClock


def create_quit():
    msg = "S" + "Q"
    msg = struct.pack('>I', len(msg)) + bytes(msg, 'UTF-8')
    return msg


def propagate_thread_function(replica_ip_str, replica_port_int, msg_str):
    propagate_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    propagate_sock.connect((replica_ip_str, replica_port_int))
    propagate_sock.sendall(msg_str)

    quit_msg = create_quit()
    propagate_sock.sendall(quit_msg)


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

    def create_propagate_message(self, send_vc_str):
        """
        create the second message we send to the server to update the value
        :param key: the key of the value that we want to update
        :param value: the value that we update the data with
        :return:
        """
        msg = "SU" + send_vc_str
        msg = struct.pack('>I', len(msg)) + bytes(msg, 'UTF-8')
        return msg


    def propagate_to_replica(self):
        # get the newly changed value
        # check if the local datastore has been changed by local client
        if not self.datastore.check_local_change():
            return
        changed_value_dic = self.datastore.locked_propagate_to_replica()
        # get the vector clock and add it up with 1
        if bool(changed_value_dic):
            send_vector_clock_str = self.vector_clock.locked_get_send_vector_clock_str()
            send_vector_clock_str = send_vector_clock_str + "|"
            # changed_value_dic is a string representation of the vector : 2:0:0:1:1:2:1
            # vector_clock_dic is a dict of {id: clock}, id is a string, clock is an int
            # we want to get 2:0:0:1:1:2:1|x:4:y:5:z:6
            changed_value_list = []
            for k, v in changed_value_dic.items():
                changed_value_list.append(str(k))
                changed_value_list.append(str(v))
            send_vector_clock_str = send_vector_clock_str + ":".join(changed_value_list)
            msg = self.create_propagate_message(send_vector_clock_str)
            # loop and send to all the replica
            replica_dic = self.vector_clock.get_replica_dic()
            # todo: maybe also use thread here
            threads = list()
            for k, v in replica_dic.items():
                replica_ip = v[0]
                replica_port = v[1]
                x = threading.Thread(target=propagate_thread_function, args=(replica_ip, replica_port, msg))
                threads.append(x)
                x.start()
            for index, thread in enumerate(threads):
                thread.join()
                """
                propagate_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                propagate_sock.connect((replica_ip, replica_port))
                propagate_sock.sendall(msg)

                quit_msg = create_quit()
                propagate_sock.sendall(quit_msg)
                """
            print("The vector clock dic to send is: ", send_vector_clock_str)
            # todo: check send to other server function
        # just remove this line: do nothing if there is no change
        #else:
        #    print("The dict is empty")

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
                print("Received value from replica: ", value_to_update)
                value_to_update_list = value_to_update.split(":")
                for i in range(len(value_to_update_list) // 2):
                    name_tmp = value_to_update_list[2 * i]
                    value_tmp = value_to_update_list[2 * i + 1]
                    self.datastore.locked_write_from_replica(name_tmp, value_tmp)

    def run(self):
        print("Start the propagation thread.")
        while True:
            event_is_set = self.e.wait(5)
            # time.sleep(5)
            # the value and vector are related, so we put all the
            # actions related to vector_clock here
            if event_is_set:
                # when new message from other replica arrives
                # the server will put the message into VectorClock
                # check the received vector clock
                # we need to clear it after process the  vector clock
                print("Now the event is set")
                if self.vector_clock.check_is_partition():
                    self.vector_clock.check_receive_from_all()
                else:
                    self.vector_clock.accept_vector_clocks()
                    # if we can accept
                    self.vector_clock.reset_vector_clock()
                    # reset the partition state
                self.e.clear()
                pass
            else:
                # the time is over, propagate to the replica
                #print("Now propagate to replica")
                if not self.vector_clock.check_is_partition():
                    self.propagate_to_replica()
