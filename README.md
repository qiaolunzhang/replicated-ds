# replicated-ds
distributed replicated data store

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
