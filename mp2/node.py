
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

    status = None
    hostname = None

    service_ip = None
    service_port = None

    connections = dict()

    port = None
    serv = None

    def __init__(self, SERVICE_IP, SERVICE_PORT, MY_PORT):

        self.status = "Initializing"
        self.host = socket.gethostname()
        print("self.host: " + str(self.host))

        self.port = MY_PORT
        self.service_ip = SERVICE_IP
        self.service_port = SERVICE_PORT


    # TODO:
    # Initialize server
    # Params: port

    def initServer(self):
        self.serv = mp2Server(self.service_ip, self.service_port, self.port)

    def startServer(self):
        self.serv.run()


    def start(self):

        self.initServer()
        self.startServer()

        self.serv.join()

        print("Node DONE")






