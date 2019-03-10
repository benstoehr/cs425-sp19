from node import Node


import numpy as np
import socketserver as ss
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

c = threading.Lock()
run_event = threading.Event()
run_event.set()

def signal_handler(signal, frame):
    #print("You pressed Control+C!")
    #client.shutdown()
    run_event.clear()
    exit(1)

signal.signal(signal.SIGINT, signal_handler)


########################
## START OF PROGRAM

HOST, ADDRESS  = socket.gethostname()
print(HOST)
print(ADDRESS)

NUM_NODES = sys.argv[1]
print("NUM NODES: " + NUM_NODES)

nodesList = dict()

## TODO:
##

SERVICE_IP = sys.argv[2]
SERVICE_PORT = sys.argv[3]

nodes = []

for i in range(NUM_NODES):

    port = int(4000 + 4000 * np.random.random())
    print("New Node with port: " + port)

    new_node = Node(SERVICE_IP, SERVICE_PORT,port)
    new_node.start()
    nodes.append(new_node)

while():

    for node in nodes:




