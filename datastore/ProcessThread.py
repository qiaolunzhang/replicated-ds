import struct
import threading


class ProcessThread(threading.Thread):
    def __init__(self, clientAddress, clientsocket, datastore,
                 num_replica, vector_clock):
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
        self.vector_clock[0] = 9
        self.vector_clock.append(3)
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
            print("Test")
            msg_len_pack = self.csocket.recv(self.RECV_MSG_LEN)
            tot_len = tot_len + len(msg_len_pack)
            print(msg_len_pack)

        msg_len = struct.unpack('>I', msg_len_pack)[0]
        msg_len = int(msg_len)
        print("This is packet has length: ", msg_len)

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
        print(msg)
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

    def process_packet_server(self, msg):
        """Actually this function can substitute the VectorHandlerThread we designed before"""
        return ""

    def run(self):
        print("Connection from: ", self.clientAddress)
        while True:
            msg = self.receive_packet()
            print(msg)
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