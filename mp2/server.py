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


    def __init__(self, port):
        Thread.__init__(self)
        self.status = "Initializing"
        self.sock = socket.socket()
        self.hostname = socket.gethostname()
        self.sock.bind((self.hostname, port))
        self.listen(10)



    def mainLoop(self):

        while(1):







