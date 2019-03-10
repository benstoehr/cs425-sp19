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

serv_ip_split = SERVICE_IP.split(":")

nodes = []

for i in range(numberOfNodes):

    nodes.append(Node(service, port))



