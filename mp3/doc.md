# cs425-spring19-mp3 Report

## Group

- mttsao2
- stoehr2 

## VM Cluster: 58

## Gitlab Repository

https://gitlab.engr.illinois.edu/mttsao2/cs425-sp19/tree/master/mp3

## How to Run the Code

Please run: 

1. `cd python`
2. `python36 greeter_server.py`
3. `python36 greeter_client.py 5` to run 5 nodes.
4. Enter the transactions in the console.

## Commit Hash

2e5be1a4223852023eec647f1511b4c320874636

## Design Document

### Lock

Each server maintains a lock dictionary locally. Once a client requests a GET or SET of an object, we put the lock request into the dictionary. If the client requests a GET and there is no SET request in the dictionary, it executes GET. Otherwise, the client has to wait for the lock released. If a client requests GET or SET and there is a SET of that object in the lock dictionary, it has to wait. The locks are released while commit or abort.

Please refer to `greeter_server.py`

```
class Greeter(mp3_pb2_grpc.GreeterServicer):
    ...
```

### Abort

The server keeps a temporary mini dictionary for each transaction. The values of the objects only update while commit. If one client aborts its transaction, the server flushes its mini dictionary and do nothing.

Please refer to `greeter_server.py`

```
class Greeter(mp3_pb2_grpc.GreeterServicer):
    ...
```

### Deadlock Detection

A coordinator monitors all operations from the servers. It keeps a dictionary of all current locks. The servers send their GET/SET/COMMIT/ABORT operations to the coordinators. When an operation message comes, it check if the operation causes any deadlocks. If yes, it sends `shouldAbort`. Otherwise, it sends `ok`. The server executes accordingly.

Please refer to `cooordinator.py`

```
class Coordinator(mp3_pb2_grpc.CoordinatorServicer):
    ...
```