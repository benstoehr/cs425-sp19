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
run_event.set()

## Define Signal Handler
def signal_handler(signal, frame):
    print("You pressed Control+C!")
    #client.shutdown()
    for node in nodes:
        node.shutdown()

    run_event.clear()
    exit(1)

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

## INFO
SERVICE_IP = sys.argv[2]
print("Service hostname: " + str(SERVICE_IP))
SERVICE_PORT = sys.argv[3]
print("Service Port: " + str(SERVICE_PORT))

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

    #nodeName = "vm" +
    #new_node = Node(SERVICE_IP, SERVICE_PORT, "vmnode"+str(i), port, run_event)
    #new_node.start()
    #nodes.append(new_node)


print("main.py: DONE!")









