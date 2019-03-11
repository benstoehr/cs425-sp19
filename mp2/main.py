from node import Node



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
import math
import random



########################
## START OF PROGRAM


c = threading.Lock()

run_event = threading.Event()
run_event.set()

def signal_handler(signal, frame):
    print("You pressed Control+C!")
    #client.shutdown()
    for node in nodes:
        node.shutdown()

    run_event.clear()
    exit(1)

signal.signal(signal.SIGINT, signal_handler)


HOST = socket.gethostname()
print(HOST)
#print(ADDRESS)

NUM_NODES = int(sys.argv[1])
print("NUM NODES: " + str(NUM_NODES))

nodesList = dict()

## TODO:
##

SERVICE_IP = sys.argv[2]
print("Service hostname: " + str(SERVICE_IP))

SERVICE_PORT = sys.argv[3]

nodes = []

count = 0

for i in range(NUM_NODES):

    port = int(4000 + 4000 * random.random())
    print("New Node with port: " + str(port))

    new_node = Node(SERVICE_IP, SERVICE_PORT, "node"+str(i), port, run_event)
    new_node.start()
    nodes.append(new_node)

while(1):
    count += 1
    # if(count % 10000000 == 0):
    #     print(count)
    pass










