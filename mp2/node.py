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

    self.serv = None
    def __init__(self, host, address):
        self.host = host
        self.address = address



    # TODO:
    # Initialize server
    # Params: port

    def initServer(self):
        self.serv = mp2Server(port)


    def connect2Service(self, port, address, TYPE=None):

        s = socket.socket()
        self.con = s.connect((port, address))

        self.service = s.getpeername()


    def sendInitiation(self):
        self.con.send('CONNECT node 1 ')






