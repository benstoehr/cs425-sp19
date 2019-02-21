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

## How to Run the Code

Please run: `Python mp1.py [name] [port] [# of users]`

e.g. `Python mp1.py Alice 4444 2`

## Commit Hash

[I'm the 40-charactorer hash]

## Design Document

### Reliability

#### Integrity

Every message received will be checked if already received by its sequence number. If the sequence number is seen, then drop the duplicate. If the sequence number does not appear yet, put the message in the hold-back queue.

dict, name of vm, array of msg & #

Please refer to:
```
Code
```

#### Agreement

A Server records the recent messages and their sequence number in case a process is failed after sending a message to some processes but not all. If there is any process finding a message is missing, it ask the server for the message.

Please refer to:
```
Code
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

When a process closes the connection, it will send an empty string to other processes. If a process received the empty string, it declares the sender process is failed.

Please refer to:

```
code
```

### Causal Ordering

Every message has its sequence number vector. The vector is assigned by its sender sequentially. When a message arrives a process, the process compares message's sequence number vector and its local sequence number vector. If the sender's sequence number is equals to its counterpart in the local vector and all other non-sender numbers are less than or equal to their correspoding counterparts in local, then the process delivers the 

Please refer to:

```
code
```