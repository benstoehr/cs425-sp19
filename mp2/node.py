
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

    # []
    transactionMessages = []
    introductionMessages = []
    serviceIntroductionMessages = []

    replyMessages = []

    nameIPPortList = []
    ipAndport2Name = dict()

    # (ip,port)
    liveAddresses = []

    # (ip, port) -> (name, status)
    pendingAddresses = dict()
    deadAddresses = []
    unknownAddresses = []

    sentMessagesByAddress = dict()
    sock = None

    def __init__(self, SERVICE_IP, SERVICE_PORT, name, MY_PORT, event):
        Thread.__init__(self)

        self.status = "Initializing"
        self.host = socket.gethostname()
        print("self.host: " + str(self.host))

        self.name = name

        self.ip = socket.gethostbyname(self.host)
        print("self.ip:" + str(self.ip))

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
        #print("read() -> got message, addr")
        if (message is not None):
            print("Got message in read() call!")
            stripped = message.strip()
            #print(str(self.name) + ": " + str(stripped))
            self.file.write(message)
        return message, addr

    # TRANSACTION 1551208414.204385 f78480653bf33e3fd700ee8fae89d53064c8dfa6 183 99 10
    # INTRODUCE node12 172.22.156.12 4444
    def handleMessage(self, message, addr):

        print("handleMessage: " + str(message))
        message = message.split()
        ip, port = message[0].split(":")
        message2send = message[1:]

        if ("TRANSACTION" in message2send):
            #print("~~got transaction from " +str(addr) + " ~~")

            self.transactionMessages.append(message2send)

            replyMessage = str(self.ip)+":"+str(self.port) + " REPLY"
            self.sock.sendto(replyMessage.encode('utf-8'), (ip, int(port)))
            self.liveAddresses.append((ip,int(port)))

        # Assume you will only get good messages
        elif ("INTRODUCE" in message2send):
            self.introductionMessages.append(message)
        elif ("REPLY" in message2send):
            #print("~~ got reply from " + str(addr) + "~~")
            pass


    def serviceRead(self):
        messageFromService = self.serv.readFromService()
        if (messageFromService is not None):
            messagesFromService = messageFromService.split("\n")
            for mess in messagesFromService:
                stripped = messageFromService.strip()
                #print(str(self.name) + ":" + str(stripped))
                self.file.write(mess)
            return messagesFromService
        return None

    def handleServiceMessage(self, message):
        message = message.split()
        if ("TRANSACTION" in message):
            print("~~got transaction from service~~")
            self.transactionMessages.append(message)
            # for tm in self.transactionMessages:
            #     print(tm)
            return
        elif ("INTRODUCE" in message):
            print("~~got introduction~~")
            self.serviceIntroductionMessages.append(message)
            return
        elif ("QUIT" in message):
            print("## Got Quit command ##")

        elif ("DIE" in message):
            print("@@ Got DIE command @@")



#######################################



    def run(self):

        timer = 0

        self.initServer()
        self.startServer()

        self.status = "running"

        while (1):

            if(self.event.isSet()):
                break

            # print("transactionMessages")
            # print(self.transactionMessages)
            #
            # print("serviceIntrodctionMessages")
            # print(self.serviceIntroductionMessages)
            #
            # print("introductionMessages")
            # print(self.introductionMessages)


            #print("Loop")
    ############### READ ALL MESSAGES ###################
        ## SERVICE STUFF
            ## Read until no messages
            while(1):
                #print("serviceRead()")
                serviceMessages = self.serviceRead()
                if(serviceMessages is None):
                    break
                for serviceMessage in serviceMessages:
                    serviceMessageType = self.messager.getMessageType(serviceMessage)
                    if(serviceMessageType is not None):
                        self.handleServiceMessage(serviceMessage)

            ######## Update list of IPs from node messages
            for serviceIntroMessage in self.serviceIntroductionMessages:
                print("Converting message to dictionary entry and adding to liveAddresses")
                vmname = serviceIntroMessage[1]
                vmIP = serviceIntroMessage[2]
                vmPort = serviceIntroMessage[3]
                if((vmIP, vmPort) not in self.ipAndport2Name.keys()):
                    # Put it in the dictionary with the name
                    self.ipAndport2Name[(vmIP, vmPort)] = (vmname, "alive")
                    # put it in the list of live addresses
                    self.liveAddresses.append((vmIP, vmPort))
            self.serviceIntroductionMessages = []

        ## NODE STUFF
            ## Read until no messages
            while(1):
                #print("read()")
                # addr = ipANDport = (ip, port)
                message, addr = self.read()
                #print("post read()")
                messageType = self.messager.getMessageType(message)
                if (messageType is not None):
                    self.handleMessage(message, addr)
                else:
                    break
            ######## Update list of IPs from node messages
            for introMessage in self.introductionMessages:
                vmname = introMessage[1]
                vmIP = introMessage[2]
                vmPort = introMessage[3]
                if((vmIP, vmPort) not in self.ipAndport2Name.keys()):
                    # Put it in the dictionary with the name
                    self.ipAndport2Name[(vmIP, vmPort)] = (vmname, "unknown")
                    self.unknownAddresses.append((vmIP, vmPort))
            self.introductionMessages = []

    ## END OF READING

        ## ADDRESS CLEAN UP
            ## Delete addresses that are stale
            for address, count in self.pendingAddresses.items():
                new_count = count + 1
                # change this to be the number of rounds before addresses are "dead"
                if (new_count > 10):
                    print(str(address) + " is dead!")
                    del self.pendingAddresses[address]
                    self.deadAddresses.append(address)
                else:
                    self.pendingAddresses[address] = new_count

    ## Figure out which addresses to send to

            # print("liveAddresses")
            # for add in self.liveAddresses:
            #     print(add)

            # Shuffle the live addresses
            random.shuffle(self.liveAddresses)

            readyToSend = None
            readyToSendLive = None
            readyToSendUnknown = None

            # from live addresses
            if(len(self.liveAddresses) < 3):
                readyToSendLive = self.liveAddresses
            else:
                readyToSendLive = self.liveAddresses[:3]

            # from unknown addresses
            if(len(self.unknownAddresses) < 2):
                readyToSendUnknown = self.unknownAddresses
            else:
                readyToSendUnknown = self.unknownAddresses[:2]

            readyToSend = readyToSendLive + readyToSendUnknown

            ## Sort the transactions
            sortedTranscations = sorted(self.transactionMessages, key=sortFunction)

            transactionsToSend = None
            if (len(sortedTranscations) < 5):
                transactionsToSend = sortedTranscations
            else:
                transactionsToSend = sortedTranscations[-5:]


            ######## WRITE TO OTHER NODES
            if(len(transactionsToSend) > 0 and len(readyToSend) > 0):
                print("transactionsToSend")
                for t in transactionsToSend:
                    print("\t" + str(t))
                print("readyToSend")
                for ip in readyToSend:
                    print("\t" + str(ip))

                for transMessage in transactionsToSend:
                    for address in readyToSend:

                        ip, port = address
                        port = int(port)

                        print("!! " + str(transMessage) + " > " + str(address) + " !!")
                        transMessage = str(self.ip) + ":" + str(self.port) + " " + str(" ".join(transMessage))
                        self.sock.sendto(transMessage.encode('utf-8'), (ip, port))

                        if(address not in self.sentMessagesByAddress.keys()):
                            self.sentMessagesByAddress[address] = [transMessage]
                        else:
                            self.sentMessagesByAddress[address] += [transMessage]

                # only remove stuff if it was sent
                for i in range(len(readyToSendLive)):
                    self.pendingAddresses[self.liveAddresses.pop()] = 0
                for i in range(len(readyToSendUnknown)):
                    self.pendingAddresses[self.unknownAddresses.pop()] = 0


                readyToSend = []
                transactionsToSend = []

            ## IDK WHY THIS IS NECESSARY
            ## RUN EVENT IS NOT PROPERLY CHECKED OTHERWISE
            #time.sleep(1)
            time.sleep(0.001)


        print("Run event unset!")
        self.shutdown()






