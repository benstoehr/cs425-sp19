# cs425-spring19-mp1 Report

## Group

- mttsao2
- stoehr2 

## VM Cluster: 58

## Gitlab Repository

https://gitlab.engr.illinois.edu/mttsao2/cs425-sp19/tree/master/mp1

## How to Run the Code

Please run: `python mp1.py [name] [port] [# of users]`

e.g. `python mp1.py Alice 4444 2`

## Commit Hash

2ee17b6d452fa2c29aa28c2e09ff2cb7f4fc1b82

## Design Document

### Connection

To establish the connections among random combination of vms, each process repeats through a while loop. In the while loop, the first step is an attempt to accept a connection. If that request times out, it moves on and sends a socket.connect() request to all of the other VMs. In order to exit this loop, a server must have two connections satisfied (one for incoming messages, and another for outgoing messages. 

We did this because we had trouble making a single connection that could be agreed upon by both applications. 

Please refer to:

```
class ServerSocket(Thread):
    ...
    def initializeConnections(self):
        ...(the logic is in this function)
```

### Reliability

Whenever a message is received, it is compared to the list of all messages that have been sent before. If it has not been seen, the message is added to a queue which will be sent out in the next iteration of the main loop.

#### Integrity

Every message received will be checked if already received by the sequence number. If the sequence number is seen, then the process drops the duplicate. If the sequence number does not appear yet, the process puts the message in the hold-back queue.

Please refer to:

```
class ServerSocket(Thread):
    ...
    def run(self):
        ...(the logic is in this function)       
```

#### Agreement

R-Multicast guarantees that every process receives the message and deliver it if a message is delivered by a correct process.

Please refer to:

```
class ServerSocket(Thread):
    ... 
    def run(self):
        ...
        while(run_event.is_set()):
            ...
            for address, (hostname, connection, status) in self.connections.items():
                if(status == 'active' and connection is not None):
                    try:
                        ...
                        if (len(receiveCheck) == 0):
                            ...
                        elif (len(receiveCheck) > 0):
                            ...
                            if (vmSender == self.vmNumber):
                                ...
                            else:
                                message = connection.recv(messageLength)
                                print(message)
                                c.acquire()
                                if(message not in sentMessages):
                                    messagesToSend.append(message)
```

#### Validity

When something is typed in on the console in `raw_input()`, it appears directly on the console. 

Please refer to:

```
while(1):
    ## CRAFTING THE MESSAGE FROM INPUT
    # message is a string
    inputMessage = raw_input()
```

### Failure Detection

When a process closes the connection, it will send an empty string to other processes by `close()`. When a process is exited it sends a final message that includes the "XXX has left chat". After that, it will close its connection. If a process received the empty string, it declares the sender process is failed.

Please refer to:

```
class ServerSocket(Thread):
    ...
    def shutdown(self):
        for address, (connection, status) in self.connections.items():
            if(status == 'active' and connection is not None):
                connection.close()

        self.sock.close()
        exit(1)
    ...
    def run(self):
        ....
        self.shutdown()
```

```
def signal_handler(signal, frame):
    print("You pressed Control+C!")
    client.shutdown()
```

```
signal.signal(signal.SIGINT, signal_handler)
```

### Causal Ordering

Every message has its sequence number vector. The vector is assigned by its sender sequentially:

`v = (ele1, ele2, ..., elen)`

For a message `m` sent from process `p1`, its vector is decided by:

`ele1`: Its sequential number on process `p1`.

`ele2`, ... , `elen`: Its local vector. Each is how many messages from process `p2`, ..., `pn` delivered on process `p1`.

When a message arrives a process, the process compares message's sequence number vector and its local sequence number vector. If the sender's sequence num ber is equals to its counterpart in the local vector and all other non-sender numbers are less than or equal to their correspoding counterparts in local, then the process delivers the message. If not, the process put the message in the queue.

After the delivery, the process checks if there are any messages in the queue also satisfies the rules. If yes, it delivers the satisfied message. 

Please refer to:

```
class ServerSocket(Thread):
    ...
    def run(self):
        ...
        count = 0
        while(run_event.is_set()):
            ... (the logic is mainly in this block)
```
