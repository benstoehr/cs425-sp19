
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
from messager import Messager


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
    messager = None

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

        filename = str(self.name) + ".txt"
        self.file = open(filename, "w+")

        self.messager = Messager()


    # TODO:
    # Initialize server
    # Params: port

    def initServer(self):
        self.serv = mp2Server(self.service_ip, self.service_port, self.name, self.port, self.event)

    def startServer(self):
        self.serv.start()

    def shutdown(self):
        print(str(self.name) + " shutting down")
        self.serv.shutdown()
        self.file.close()
        print(str(self.name) + " Exiting")
        self.status = "shutdown"

    def read(self):
        message = self.serv.read()
        if (message == "0"):
            # print("No message from Nodes")
            pass
        else:
            stripped = message.strip()
            print("New Message: " + str(stripped))
            self.file.write(message)

        return message

    def serviceRead(self):
        messageFromService = self.serv.readFromService()
        if (messageFromService == "0"):
            # print("No message from Service")
            pass
        else:
            stripped = messageFromService.strip()
            print(str(stripped))
            self.file.write(messageFromService)

        return messageFromService

#######################################

    def run(self):

        self.initServer()
        self.startServer()

        while (self.event.is_set()):

            ############### READ ALL MESSAGES ###################
            serviceMessage = self.serviceRead()
            message = self.read()



            messageType = self.messager.getMessageType(message)
            ######## WRITE TO OTHER NODES

        print("Run event unset!")






