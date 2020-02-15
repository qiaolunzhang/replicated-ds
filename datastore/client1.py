import socket
import struct

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

def create_quit():
    msg = "C" + "Q"
    msg = struct.pack('>I', len(msg)) + bytes(msg, 'UTF-8')
    return msg

if __name__ == "__main__":
    SERVER = "127.0.0.1"
    PORT = 8080
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((SERVER, PORT))
    #in_data = client.recv(1024)
    #print("From Server: ", in_data.decode())

    key = "x"
    value = str(3)
    message = create_write(key, value)
    #client.sendall(bytes(message, 'UTF-8'))
    print(message)
    client.sendall(message)
    #in_data = client.recv(2048)

    message = create_quit()
    client.sendall(message)

    client.close()