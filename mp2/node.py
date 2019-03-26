
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
import random

from server import mp2Server
from messager import Messager


def sortFunction(x):
    return x[1]


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

    nameIPPortList = []
    ipAndport2Name = dict()

    liveAddresses = []
    pendingAddresses = dict()
    deadAddresses = []
    unknownAddresses = []

    sock = None

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

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

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


#### List manipulation
    def getNameAndPortFromIP(self):
        pass

###### READING FUNCTIONS

    def read(self):
        message, addr = self.serv.read()
        if (message is not None):
            stripped = message.strip()
            print(str(self.name) + ": " + str(stripped))
            self.file.write(message)
        return message, addr


    # TRANSACTION 1551208414.204385 f78480653bf33e3fd700ee8fae89d53064c8dfa6 183 99 10
    # INTRODUCE node12 172.22.156.12 4444
    def handleMessage(self, message, addr):
        message = message.split()
        if ("TRANSACTION" in message):
            self.transactionMessages.append(message)
        # Assume you will only get good messages
        elif ("INTRODUCTION" in message):
            self.introductionMessages.append(message)
        elif ("REPLY" in message):
            #self.pendingAddresses.remove()
            pass

    def serviceRead(self):
        messageFromService = self.serv.readFromService()
        if (messageFromService is not None):
            stripped = messageFromService.strip()
            print(str(self.name) + ":" + str(stripped))
            self.file.write(messageFromService)

        return messageFromService

    def handleServiceMessage(self, message):
        message = message.split()
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

        while (1):

            if(self.event.isSet()):
                break

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
                # addr = ipANDport = (ip, port)
                message, addr = self.read()
                messageType = self.messager.getMessageType(message)
                if (messageType is not None):
                    self.handleMessage(message, addr)
                else:
                    break

            ######## Update list of IPs
            for introMessage in self.introductionMessages:
                vmname = introMessage[1]
                vmIP = introMessage[2]
                vmPort = introMessage[3]
                if((vmIP, vmPort) not in self.ipAndport2Name.keys()):
                    # Put it in the dictionary with the name
                    self.ipAndport2Name[(vmIP, vmPort)] = vmname
                    # maybe not?
                    # put it in the list of live addresses
                    #self.liveAddresses.append((vmIP, vmPort))

            self.introductionMessages = []

            # Shuffle the live addresses
            random.shuffle(self.liveAddresses)

            readyToSend = None
            if(len(self.liveAddresses) < 3):
                readyToSend = self.liveAddresses
            else:
                readyToSend = self.liveAddresses[:3]


            ## Sort the transactions
            sortedTranscations = sorted(self.transactionMessages, key=sortFunction)
            transactionsToSend = None
            if (len(sortedTranscations) < 5):
                transactionsToSend = sortedTranscations
            else:
                transactionsToSend = sortedTranscations[:-5]


            ######## WRITE TO OTHER NODES
            for address in readyToSend:
                for transMessage in transactionsToSend:
                    self.sock.sendto(transMessage, address)

            ## Delete addresses that are stale
            for address, count in self.pendingAddresses.items():
                new_count = count + 1
                # change this to be the number of rounds before addresses are "dead"
                if(new_count > 10):
                    print(str(address) + " is dead!")
                    del self.pendingAddresses[address]
                    self.deadAddresses.append(address)
                else:
                    self.pendingAddresses[address] = new_count

            for i in range(len(readyToSend)):
                self.pendingAddresses[self.liveAddresses.pop()] = 0

            readyToSend = []
            transactionsToSend = []

            ## IDK WHY THIS IS NECESSARY
            ## RUN EVENT IS NOT PROPERLY CHECKED OTHERWISE
            time.sleep(1)
            #time.sleep(0.0001)


        print("Run event unset!")
        self.shutdown()






