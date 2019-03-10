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


HOST, ADDRESS  = socket.gethostname()
node = Node(HOST, ADDRESS)

numberOfNodes = sys.argv[1]

nodes = []

for i in range(numberOfNodes):
    nodes.append(Node())



