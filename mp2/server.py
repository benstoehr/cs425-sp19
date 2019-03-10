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

class mp2Server(Thread):

    status = None

    hostname = None
    port = None

    sock = None
    service_ip = None
    service_port = None

    serviceSocket = None

    connections = []

    def __init__(self, SERVICE_IP, SERVICE_PORT, MY_PORT):
        Thread.__init__(self)

        self.service_ip = SERVICE_IP
        self.service_port = SERVICE_PORT

        self.status = "Initializing"
        self.sock = socket.socket()
        self.hostname = socket.gethostname()
        print("hostname: " + str(self.hostname))

        self.sock.bind((self.hostname, MY_PORT))
        self.sock.listen(10)

    def acceptConnection(self):

        ip, port = self.sock.accept()


    def connect2Service(self):

        self.serviceSocket = socket.socket()
        self.con = self.serviceSocket.connect((self.service_ip, self.service_port))

        self.service = self.con.getpeername()

        print("peername: " +str(self.service))


    def run(self):

        self.connect2Service()
        self.con.send('CONNECT node1 ')
        firstMessage = self.con.recv(1024)
        print("firstMessage: " +str(firstMessage))

        count = 0

        while(1):
            print("Count: " + count)f
            count += 1
            time.sleep(1)



















