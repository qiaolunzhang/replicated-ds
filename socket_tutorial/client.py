import socket
import struct
SERVER = "127.0.0.1"
PORT = 8080
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((SERVER, PORT))
client.sendall(bytes("This is from Client", 'UTF-8'))

while True:
    in_data = client.recv(1024)
    print("From Server: ", in_data.decode())
    #out_data = input()
    key = "x"
    value = str(3)
    message = struct.pack('>I', len(key)) + \
              struct.pack('>I', len(value)) + bytes(key, 'UTF-8') + bytes(value, 'UTF-8')
    #client.sendall(bytes(message, 'UTF-8'))
    client.sendall(message)
    if message == 'bye':
        break
client.close()