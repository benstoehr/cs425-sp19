
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

    transactionMessages = []
    introductionMessages = []
    replyMessages = []


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

###### READING FUNCTIONS

    def read(self):
        message = self.serv.read()
        if (message == "0"):
            # print("No message from Nodes")
            pass
        else:
            stripped = message.strip()
            print(str(self.name) + ": " + str(stripped))
            self.file.write(message)

        return message

    def handleMessage(self, message):
        if ("TRANSACTION" in message):
            self.transactionMessages.append(message)
        elif ("INTRODUCTION" in message):
            self.introductionMessages.append(message)
        elif ("REPLY" in message):
            pass

    def serviceRead(self):
        messageFromService = self.serv.readFromService()
        if (messageFromService == "0"):
            # print("No message from Service")
            pass
        else:
            stripped = messageFromService.strip()
            print(str(self.name) + ":" + str(stripped))
            self.file.write(messageFromService)

        return messageFromService

    def handleServiceMessage(self, message):
        if ("TRANSACTION" in message):
            self.transactionMessages.append(message)
        elif ("INTRODUCTION" in message):
            self.introductionMessages.append(message)
        elif ("QUIT" in message):
            #TODO:
            pass
        elif ("DIE" in message):
            #TODO:
            pass


#######################################

    def run(self):

        self.initServer()
        self.startServer()

        self.status = "running"

        while (not self.event.is_set()):

            #print("Loop")
            ############### READ ALL MESSAGES ###################
            ## Read until no messages
            while(1):
                #print("serviceRead()")
                serviceMessage = self.serviceRead()
                serviceMessageType = self.messager.getMessageType(serviceMessage)
                if(serviceMessageType is not None):
                    self.handleServiceMessage(serviceMessage)
                else:
                    break

            ## Read until no messages
            while(1):
                #print("read()")
                message = self.read()
                messageType = self.messager.getMessageType(message)
                if (messageType is not None):
                    self.handleMessage(message)
                else:
                    break

            ######## WRITE TO OTHER NODES


            time.sleep(0.01)


        print("Run event unset!")
        self.shutdown()






