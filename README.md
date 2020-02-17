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

### 20200217

- The class VectorHandlerThread.py: in this class, implement both the functions of
sending and receiving between relicas

- VectorClocks.py: the operation about how wto solve vector clocks

- Server.py: operations about issue the event when we receive vector clock from other replicas

- One test Client.py: a client that only write one value to the server

#### Notes

- if a replica wants to join, we can assign an integer to it, the
integer is larger than any other id of the replicas in the  system.
We just keep all the ids that are used before. And use the id that
is bigger than that.
