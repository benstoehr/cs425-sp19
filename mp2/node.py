
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


class Node(Thread):

    #global run_event

    status = None
    hostname = None

    service_ip = None
    service_port = None

    connections = dict()

    name = None
    port = None
    serv = None

    file = None

    def __init__(self, SERVICE_IP, SERVICE_PORT, name, MY_PORT, event):
        Thread.__init__(self)

        self.status = "Initializing"
        self.host = socket.gethostname()
        print("self.host: " + str(self.host))

        self.name = name
        self.port = MY_PORT
        self.service_ip = SERVICE_IP
        self.service_port = SERVICE_PORT
        self.event = event

        filename = str(self.name) + "txt"
        self.file = open(filename, "w+")


    # TODO:
    # Initialize server
    # Params: port

    def initServer(self):
        self.serv = mp2Server(self.service_ip, self.service_port, self.name, self.port, self.event)

    def startServer(self):
        self.serv.start()

    def shutdown(self):
        self.serv.shutdown()

    def run(self):

        self.initServer()
        self.startServer()

        while (self.event.is_set()):

            #print("Node DONE initializing!")

            messageFromService = self.serv.readFromService()
            if(messageFromService == "0"):
                #print("No message from Service")
                pass
            else:
                print("Service: " + str(messageFromService))
                self.file.write(messageFromService)
            message = self.serv.read()
            if (message == "0"):
                #print("No message from Nodes")
                pass
            else:
                print("New Message: " + str(message))
                self.file.write(message)

            time.sleep(0.5)



        print("Run event unset!")






