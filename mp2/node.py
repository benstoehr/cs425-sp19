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
from server import mp2Server


class Node(object):

    hostname = None

    service_ip = None
    service_port = None

    connections = dict()

    port = None
    serv = None

    def __init__(self, SERVICE_IP, SERVICE_PORT, MY_PORT):

        self.host = socket.gethostname()
        print("self.host: " + str(self.host))

        self.port = MY_PORT
        self.service_ip = SERVICE_IP
        self.service_port = SERVICE_PORT


    # TODO:
    # Initialize server
    # Params: port

    def initServer(self):
        self.serv = mp2Server(self.port)



    def sendInitiation(self):
        self.con.send('CONNECT node 1 ')







