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

add the interaction with the database, solve the data to database
or load data from database


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

#### Communication between sever and server

- If we update data, it is defined as follows: 

```
SUsender_id:id1:value:id2:value:id3:value|x:3:y:4:z:5
```
So it start with S and U, S represents that it is the message from server, U represents
that it is a message to update data.

- some messages in ProcessThread.py, in function process_packet_server, in this class,
we just receive message and save it in the class VectorClock

- VectorHandlerThread: we handle new thread in this class

### 2020/02/19
Actually, only looking at changed value, may have a problem, that
is we will go to an infinite loop!
Because once I changed the value, I send to the other replica. This will 
makes the other replica send the value to me.

There are two members in CausalDatastore:

- self.value_dic{}
- 

maybe just need to propagate local change!!!