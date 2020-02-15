# replicated-ds
distributed replicated data store

## Definition of messages

### direction of the message
- client -> server
- server -> client
- server -> server

the message from server is marked with "S"
the message from client is marked with "C"

### message type

*Client -> server*

- Write: "W"
- Modify: "M"
- Read: "R"
- Quit: "Q"

*Server -> client*

- value: "V"

*Server -> Server*

- Update: "U"
- Find: "F"

### For client

## Server
Receive the packets from:
1. clients
2. other replicas

The server will open a new thread

### vector clock

### mutex
https://stackoverflow.com/questions/3310049/proper-use-of-mutexes-in-python

## Client
1. connect to the server
2. read and write

## Todo
### data store

### how to avoid race condition

when we send a message to the server, we need to mark "Read", "Write", "Modify"

https://realpython.com/intro-to-python-threading/
