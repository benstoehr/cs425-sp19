from node import Node

#import socketserver as ss
import parser
import socket

# IMPORT STATEMENTS
import socket
import sys
from threading import Thread
import threading
import time
import logging
import fcntl, os
import errno
import signal
import math
import random



########################
## START OF PROGRAM

## USAGE
## python main.py <number of nodes> <service IP> <service port>

c = threading.Lock()

run_event = threading.Event()
run_event.clear()

## Define Signal Handler
def signal_handler(sig, frame):
    print("You pressed Control+C!")
    #client.shutdown()
    # for node in nodes:
    #     node.event.clear()

    run_event.set()
    done = True
    #exit(1)

## Setup Signal Handler for clean Exit
signal.signal(signal.SIGINT, signal_handler)

HOST = socket.gethostname()
print(HOST)
#print(ADDRESS)

NUM_NODES = int(sys.argv[1])
print("NUM NODES: " + str(NUM_NODES))

nodesList = dict()

## TODO:
##

## SERVICE INFO
SERVICE_IP = sys.argv[2]
print("Service hostname: " + str(SERVICE_IP))
SERVICE_PORT = sys.argv[3]
print("Service Port: " + str(SERVICE_PORT))

## SELF INFO
hostname = HOST.strip()
hostnameSplit = hostname.split("-")
print(hostnameSplit)

vmNumber = 0
if(hostnameSplit[0] == "sp19"):
    vmWithIllinoisDotEDU = hostnameSplit[3]
    vmNumber = vmWithIllinoisDotEDU.split(".")[0]

portNumbers = []
nodes = []

count = 0

for i in range(NUM_NODES):

    port = int(4000 + 4000 * random.random())

    # Can't have two of the same port
    while(port in portNumbers):
        port = int(4000 + 4000 * random.random())

    portNumbers.append(port)
    print("New Node with port: " + str(port))

    nodeName = "vm" + str(vmNumber) + "node" + str(i)
    print("nodeName: " + str(nodeName))

    new_node = Node(SERVICE_IP, SERVICE_PORT, nodeName, port, run_event)
    new_node.start()
    nodes.append(new_node)


done = False

while(not done):

    shutdownCheck = True

    for node in nodes:

        stat = node.status
        if(node.status == "shutdown"):
            #print(str(node.name) + ": " + str(node.status))
            nodes.remove(node)
            pass
        else:
            shutdownCheck = False

    if(shutdownCheck == True):
        break

    time.sleep(0.001)



time.sleep(10)
print("main.py: DONE!")
exit(1)







