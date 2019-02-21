Your report should include the following information:

- The netids of the people in your group
- The number of your VM cluster
- The URL of your gitlab repository (e.g. https://gitlab.engr.illinois.edu/jsmith2/425-mp1
- Instructions for building and running your code. Note that the TAs will be running your code on your VMs but under their own accounts, so make sure the instructions do not depend on anything installed inside your home directory (or specify how to install it)
- The full commit hash of the revision that you want to be graded. You can see the revision on the command line with git rev-parse HEAD or in GitLab by selecting the "Copy SHA hash" button. Make sure to include the full 40-character hash, not the 8-character abbreviation GitLab displays.  

# cs425-spring19-mp1 Report

## Group

- mttsao2
- stoehr2 

## VM Cluster: 58

## Gitlab Repository

https://gitlab.engr.illinois.edu/mttsao2/cs425-sp19/tree/master/mp1

## How to Run the Code

Please run: `Python mp1.py [name] [port] [# of users]`

e.g. `Python mp1.py Alice 4444 2`

## Commit Hash

[I'm the 40-character hash]

## Design Document

### Reliability

#### Integrity

Every message received will be checked if already received by the sequence number. If the sequence number is seen, then the process drops the duplicate. If the sequence number does not appear yet, the process puts the message in the hold-back queue.

Please refer to:

```
class ServerSocket(Thread):
    ...

```

```
class ClientSocket():
    ...
    
```

#### Agreement

R-Multicast guarantees that every process receives the message and deliver it if a message is delivered by a correct process.

Please refer to:
```
class ServerSocket(Thread):
    ...
```

```
class ClientSocket():
    ...

```

#### Validity

When something is typed in on the console in `raw_input()`, it appears directly on the console. 

Please refer to:

```
class ClientSocket():
    ...
    def mainLoop(self):
       while(1):
            msg = raw_input("> ")
```

### Failure Detection

When a process closes the connection, it will send an empty string to other processes by `close()`. If a process received the empty string, it declares the sender process is failed.

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
class ClientSocket():
    ...
    def shutdown(self):
    for serverName, (connection, status) in self.connections.items():
        if(status == 'active' and connection is not None):
            connection.close()

    self.sock.close()
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

ele1: Its sequential number on process `p1`.

ele2, ... , elen: Its local vector. Each is how many messages from process `p2`, ..., `pn` delivered on process `p1`.

When a message arrives a process, the process compares message's sequence number vector and its local sequence number vector. If the sender's sequence number is equals to its counterpart in the local vector and all other non-sender numbers are less than or equal to their correspoding counterparts in local, then the process delivers the message. If not, the process put the message in the queue.

After the delivery, the process checks if there are any messages in the queue also satisfies the rules. If yes, it delivers the satisfied message. 

Please refer to:

```
class ServerSocket(Thread):
    ...
    def run(self):
        ...
        count = 0

        while(run_event.is_set()):
        ...
            count = 0
            for address, (connection, status) in self.connections.items():
            ... (the logic is in this block)
```