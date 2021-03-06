import socket
import threading
import struct
import logging
import time
from threading import Event
from datastore.CausalDatastore import CausalDataStore
from datastore.ProcessThread import ProcessThread
from datastore.VectorClock import VectorClock


def create_quit():
    msg = "S" + "Q"
    msg = struct.pack('>I', len(msg)) + bytes(msg, 'UTF-8')
    return msg


class ControlThread(threading.Thread):
    def __init__(self, datastore: CausalDataStore, vector_clock: VectorClock, event: Event):
        threading.Thread.__init__(self)
        self.datastore = datastore
        self.vector_clock = vector_clock
        self.RECV_BUFFER = 4096
        self.RECV_MSG_LEN = 4
        self.join_client = None
        self.e = event

    def create_join(self):
        msg = "S" + "J"
        host, port = self.vector_clock.get_host_port()
        msg = msg + "|" + host + ":" + str(port)
        msg = struct.pack('>I', len(msg)) + bytes(msg, 'UTF-8')
        return msg

    def receive_packet(self):
        if self.join_client is None:
            return ""
        tot_len = 0
        msg_len_pack = b""
        msg = ""
        # todo: add more control for length
        while tot_len < self.RECV_MSG_LEN:
            # print("Test")
            msg_len_pack = self.join_client.recv(self.RECV_MSG_LEN)
            tot_len = tot_len + len(msg_len_pack)

        msg_len = struct.unpack('>I', msg_len_pack)[0]
        msg_len = int(msg_len)

        tot_len = 0
        while tot_len < msg_len:
            if (msg_len - tot_len) > self.RECV_BUFFER:
                msg = self.join_client.recv(self.RECV_BUFFER)
            else:
                msg = self.join_client.recv(msg_len - tot_len)
            tot_len = tot_len + len(msg)
        msg = msg.decode('UTF-8')
        return msg

    def join_datastore(self, server_ip, server_port):
        """
        Join the datastore, need to add function to VectorClock
        Initialize
        vector_clock_dic
        replica_dic
        :return:
        """
        join_msg = self.create_join()
        self.join_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.join_client.connect((server_ip, server_port))
        self.join_client.sendall(join_msg)
        msg = self.receive_packet()
        print(msg)
        quit_msg = create_quit()
        self.join_client.sendall(quit_msg)
        self.join_client.close()
        #senderid:new_id | id1: ip:port | id2: ip2:port
        msg_list = msg.split("|")
        print(msg_list)
        sender_new_id_list = msg_list[0][1:].split(":")
        local_id = int(sender_new_id_list[1])
        #replica_id_tmp = int(sender_new_id_list[1])
        vc_dic = {}
        #vc_dic[replica_id_tmp] = [server_ip, server_port]
        for element in msg_list[1:]:
            element_list = element.split(":")
            vc_dic[int(element_list[0])] = [element_list[1], int(element_list[2])]

        self.vector_clock.init_vector_clock_dic(vc_dic, local_id, join=True)

    def leave_datastore(self, server_ip, server_port):
        """
        Leave the datastore
        :return:
        """
        self.vector_clock.set_leave_replica(server_ip, server_port)
        self.e.set()

    def run(self):
        while True:
            command = input("Please type your command: ")
            command_list = command.split(" ")
            if command == "show datastore":
                print(self.datastore.value_dic)
            elif command_list[0] == "join":
                # join 192.168.138.1 80
                self.join_datastore(command_list[1], int(command_list[2]))
            elif command_list[0] == "leave":
                self.leave_datastore(command_list[1], int(command_list[2]))
            elif command == "show replica":
                print("Total replica is: ", self.vector_clock.get_replica_dic())
                print("The leaved replica is: ", self.vector_clock.get_leaved_replica())
            elif command == "show vector clock":
                print(self.vector_clock.vector_clock_dic)
            elif command == "show local_id":
                print(self.vector_clock.get_local_id())
            elif command == "show partition":
                # if the result is True, means that this replica is not connected with other replica
                print(self.vector_clock.is_partition)
            elif command == "show received_vc_dict":
                print(self.vector_clock.received_vc_dict)
            elif command == "show join_syn_dic":
                print(self.vector_clock.join_syn_dic)
