import struct
import threading
from threading import Event
from datastore.VectorClock import VectorClock

class ProcessThread(threading.Thread):
    def __init__(self, clientAddress, clientsocket, datastore,
                 num_replica, vector_clock: VectorClock, event: Event):
        threading.Thread.__init__(self)
        self.datastore = datastore
        self.clientAddress = clientAddress
        self.csocket = clientsocket
        self.RECV_BUFFER = 4096
        self.RECV_MSG_LEN = 4
        self.from_client = False
        self.from_server = False
        self.num_replica = num_replica
        self.vector_clock = vector_clock
        self.e = event
        #self.vector_clock[0] = 9
        #self.vector_clock.append(3)
        #self.local_changed_dic = {}
        print("New connection added: ", clientAddress)

    def get_message_value_to_client(self, key, value):
        msg = "S" + key + ":" + value
        msg = struct.pack('>I', len(msg)) + bytes(msg, 'UTF-8')
        return msg

    def receive_packet(self):
        tot_len = 0
        msg_len_pack = b""
        msg = ""
        # todo: add more control for length
        while tot_len < self.RECV_MSG_LEN:
            #print("Test")
            msg_len_pack = self.csocket.recv(self.RECV_MSG_LEN)
            tot_len = tot_len + len(msg_len_pack)
            #print(msg_len_pack)

        msg_len = struct.unpack('>I', msg_len_pack)[0]
        msg_len = int(msg_len)
        # todo: remove to get packet output
        #print("This is packet has length: ", msg_len)

        tot_len = 0
        while tot_len < msg_len:
            #msg = self.csocket.recv(self.RECV_BUFFER)
            if (msg_len - tot_len) > self.RECV_BUFFER:
                msg = self.csocket.recv(self.RECV_BUFFER)
            else:
                msg = self.csocket.recv(msg_len-tot_len)
            tot_len = tot_len + len(msg)
        msg = msg.decode('UTF-8')
        return msg

    def process_packet_client(self, msg):
        #print(msg)
        if msg[0] == "Q":
            return "quit"
        elif msg[0] == "W":
            # e.g. x:3
            msg = msg[1:].split(":")
            key = msg[0]
            value = msg[1]
            # not necessarily to be integer
            #value = int(msg[1])
            self.datastore.locked_write(key, value)
        elif msg[0] == "U":
            self.datastore.lock.acquire()
            key = msg[1:]
            value = self.datastore.read(key)
            value = str(value)
            message_to_client = self.get_message_value_to_client(key, value)
            self.csocket.sendall(message_to_client)
            # todo: may also change this one to use packet length
            #value_update = self.csocket.recv(self.RECV_BUFFER)
            value_update = self.receive_packet()
            value_update = value_update[1:].split(":")[1]
            self.datastore.write(key, value_update)
            self.datastore.lock.release()

        return ""

    def get_message_to_new_replica(self, replica_msg):
        msg = "S" + replica_msg
        msg = struct.pack('>I', len(msg)) + bytes(msg, 'UTF-8')
        return msg

    def process_packet_join(self, host_val, port_val):
        replica_str = self.vector_clock.get_replica_str()
        new_id = self.vector_clock.assign_new_id()
        # add the new replica to vector_clock
        self.vector_clock.add_new_replica_to_vector_clock(new_id, 0, host_val, port_val)

        # send back localid:new_id|id1:ip:port|id2:ip2:port
        local_id_str = str(self.vector_clock.get_local_id())
        replica_msg = local_id_str + ":" + str(new_id) + "|" + replica_str
        replica_msg = self.get_message_to_new_replica(replica_msg)
        self.csocket.sendall(replica_msg)

        self.vector_clock.put_leader_dic(new_id, host_val, int(port_val))
        #self.vector_clock.put_leader_dic(new_id, self.)

    def process_packet_server(self, msg):
        """Actually this function can substitute the VectorHandlerThread we designed before"""
        print(msg)
        # update the value
        if msg[0] == "Q":
            return "quit"
        if msg[0] == "U":
            # sender_id:id1:value:id2:value:id3:value|x:3:y:4:z:5
            msg = msg[1:].split("|")
            if len(msg) == 2:
                self.vector_clock.locked_add_received_vc(msg[0], msg[1])
            # 2:0:0:1:1:2:1|x:4:y:5:z:6|JL3:192.168.221.1:8080
            elif len(msg) == 3 and msg[2][0:2] == "JL":
                if self.vector_clock.check_is_partition():
                    # tell him that there is a new message
                    # self.vector_clock.do_something()
                    #self.vector_clock.locked_add_received_vc(msg[0], msg[1])
                    clock = msg[0]
                    sender_id = clock.split(":")[0]
                    self.vector_clock.add_join_syn_dic(sender_id, msg[2][2:], msg[0])
                else:
                    self.vector_clock.locked_add_received_vc(msg[0], msg[1])
                    new_replica_str = msg[2][2:]
                    new_replica_list = new_replica_str.split(":")
                    self.vector_clock.put_follower_dic(int(new_replica_list[0]),
                                                       new_replica_list[1], int(new_replica_list[2]))
                    # add the new client
                    self.vector_clock.add_new_replica_to_vector_clock(int(new_replica_list[0]), 0,
                                                                      new_replica_list[1], int(new_replica_list[2]))
            elif len(msg) == 3 and msg[2][0:2] == "JF":
                # sender_id:id1:value:id2:value:id3:value|x:3:y:4:z:5|JF IP:new_replica_ip:new_replica_port
                # actually it's the message received by the follower
                if self.vector_clock.check_is_partition():
                    # log that there is a new message
                    #self.vector_clock.locked_add_received_vc(msg[0], msg[1])
                    clock = msg[0]
                    sender_id = clock.split(":")[0]
                    self.vector_clock.add_join_syn_dic(sender_id, msg[2][2:], msg[0])
                else:
                    self.vector_clock.locked_add_received_vc(msg[0], msg[1])
                    #self.set_received_start_vc(msg[0], msg[2])
            self.e.set()
        # join the data store
        elif msg[0] == "J":
            host_port_list = msg[2:].split(":")
            host = host_port_list[0]
            port = host_port_list[1]
            self.process_packet_join(host, port)
            #replica_str = self.vector_clock.get_replica_str()
            #replica_msg = self.get_message_to_new_replica(replica_str)
            #self.csocket.sendall(replica_msg)
            # store another dict in the VectorClock
        # leave the data store
        elif msg[0] == "L":
            msg = msg[1:].split(":")
            leaved_id = msg[0]
            self.vector_clock.remove_replica(leaved_id)
            pass
        elif msg[0] == "F":
            pass
        return ""

    def run(self):
        print("Connection from: ", self.clientAddress)
        while True:
            msg = self.receive_packet()
            # todo: remove to print the received message
            #print(msg)
            # todo: how to keep vector clock data from other server
            result = ""
            if msg[0] == "C":
                self.from_client = True
                result = self.process_packet_client(msg[1:])
            elif msg[0] == "S":
                self.from_server = True
                result = self.process_packet_server(msg[1:])
            if result == "quit":
                break

        print("Client at ", self.clientAddress, " disconnected...")
        print(self.datastore.value_dic)