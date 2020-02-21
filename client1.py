import socket
import struct
import threading
import time

class Client:
    def __init__(self):
        self.SERVER_IP = "127.0.0.1"
        self.SERVER_PORT = 8080

    def load_config(self):
        try:
            with open('datastore/config/client.conf') as f:
                for line in f:
                    if line[0] != '#':
                        line = line.split()
                        if line[0] == 'server_ip':
                            self.host = line[1]
                            self.port = int(line[2])
        except Exception as e:
            print(e)

    def write(self, _key, _value):
        pass

def create_write(key, value):
    """
    create the message to sent when we write the datastore
    :param key: a string
    :param value: a string
    :return:
    """
    msg = "C" + "W" + key + ":" + value
    msg = struct.pack('>I', len(msg)) + bytes(msg, 'UTF-8')
    return msg

def create_update_get(key):
    """
    :param key: the key of the value that we want to update
    :return: the string to send to the server
    """
    msg = "C" + "U" + key
    msg = struct.pack('>I', len(msg)) + bytes(msg, 'UTF-8')
    return msg


def create_update_change(key, value):
    """
    create the second message we send to the server to update the value
    :param key: the key of the value that we want to update
    :param value: the value that we update the data with
    :return:
    """
    msg = "C" + key + ":" + value
    msg = struct.pack('>I', len(msg)) + bytes(msg, 'UTF-8')
    return msg


def create_quit():
    msg = "C" + "Q"
    msg = struct.pack('>I', len(msg)) + bytes(msg, 'UTF-8')
    return msg

def receive_packet(client):
    RECV_MSG_LEN = 4
    RECV_BUFFER = 2048
    tot_len = 0
    msg_len_pack = b""
    msg = ""
    # todo: add more control for length
    while tot_len < RECV_MSG_LEN:
        print("Test")
        msg_len_pack = client.recv(RECV_MSG_LEN)
        tot_len = tot_len + len(msg_len_pack)
        print(msg_len_pack)

    msg_len = struct.unpack('>I', msg_len_pack)[0]
    msg_len = int(msg_len)
    print("This is packet has length: ", msg_len)

    tot_len = 0
    while tot_len < msg_len:
        #msg = self.csocket.recv(self.RECV_BUFFER)
        if (msg_len - tot_len) > RECV_BUFFER:
            msg = client.recv(RECV_BUFFER)
        else:
            msg = client.recv(msg_len-tot_len)
        tot_len = tot_len + len(msg)
    msg = msg.decode('UTF-8')
    print(msg)
    return msg

def loop_update1(index, server_ip, server_port, loop_time_value):
    #SERVER = "127.0.0.1"
    #PORT = 8080
    client1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client1.connect((server_ip, server_port))
    for i in range(loop_time_value):
        key = "x"
        message = create_update_get(key)
        # send the message to request for the data
        client1.sendall(message)
        # value = client.recv(1024)
        key_value = receive_packet(client1)
        key_value = key_value[1:].split(":")
        key_receive = key_value[0]
        value_receive = key_value[1]

        print(key_receive)
        if value_receive == "":
            value = 1
        else:
            value = int(value_receive) + 1
        message = create_update_change(key, str(value))
        client1.sendall(message)
    message = create_quit()
    client1.sendall(message)

def loop_update2(index, server_ip, server_port, loop_time_value):
    #SERVER = "127.0.0.1"
    #PORT = 8080
    client2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client2.connect((server_ip, server_port))
    for i in range(loop_time_value):
        key = "x"
        message = create_update_get(key)
        # send the message to request for the data
        client2.sendall(message)
        # value = client.recv(1024)
        key_value = receive_packet(client2)
        key_value = key_value[1:].split(":")
        key_receive = key_value[0]
        value_receive = key_value[1]

        print(key_receive)
        if value_receive == "":
            value = -1
        else:
            value = int(value_receive) - 1

        message = create_update_change(key, str(value))
        client2.sendall(message)
    message = create_quit()
    client2.sendall(message)

def load_config():
    try:
        with open('datastore/config/client.conf') as f:
            for line in f:
                if line[0] != '#':
                    line = line.split()
                    if line[0] == 'server_ip':
                        host = line[1]
                        port = int(line[2])
    except Exception as e:
        print(e)
    return host, port


if __name__ == "__main__":
    #SERVER_IP = "127.0.0.1"
    #SERVER_PORT = 8080
    SERVER_IP, SERVER_PORT = load_config()
    threads = list()
        #logging.info("Main: create and start thread %d.", index)

    loop_time1 = 3
    x = threading.Thread(target=loop_update1, args=(1, SERVER_IP, SERVER_PORT, loop_time1))
    threads.append(x)
    x.start()

    loop_time2 = 2
    x = threading.Thread(target=loop_update2, args=(2, SERVER_IP, SERVER_PORT, loop_time2))
    threads.append(x)
    x.start()

    for index, thread in enumerate(threads):
        #logging.info("Main: before joining thread %d.", index)
        thread.join()
        #logging.info("Main: thread %d done", index)

    """
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    client_socket.connect((SERVER_IP, SERVER_PORT))

    key = "x"
    value = str(3)
    message = create_write(key, value)
    print(message)
    client_socket.sendall(message)

    for i in range(3):
        time.sleep(0.1)
        key = "x"
        message = create_update_get(key)
        # send the message to request for the data
        client_socket.sendall(message)
        #value = client.recv(1024)
        key_value = receive_packet(client_socket)
        key_value = key_value[1:].split(":")
        key_receive = key_value[0]
        value_receive = key_value[1]

        print(key_receive)
        value = int(value_receive) - 1
        message = create_update_change(key, str(value))
        client_socket.sendall(message)

    """

    """
    message = create_quit()
    client_socket.sendall(message)

    client_socket.close()
    """