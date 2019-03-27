
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
    receivedMessagesByAddress = dict()

    sock = None

    def __init__(self, SERVICE_IP, SERVICE_PORT, name, MY_PORT, event):
        Thread.__init__(self)

        self.status = "Initializing"
        self.host = socket.gethostname()
        print("self.host: " + str(self.host))

        self.name = name
        print("name: " +str(self.name))
        self.vmNumber = int(self.name[8])

        self.ip = socket.gethostbyname(self.host)
        print("self.ip:" + str(self.ip))

        self.port = MY_PORT
        self.service_ip = SERVICE_IP

        self.service_port = SERVICE_PORT

        self.event = event

        filename = str(self.name) + ".txt"
        #self.file = open(filename, "w+")
        logging.basicConfig(filename=filename, level=logging.DEBUG)

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
        #self.file.close()
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
            # self.file.write(message)
        return message, addr

    # TRANSACTION 1551208414.204385 f78480653bf33e3fd700ee8fae89d53064c8dfa6 183 99 10
    # INTRODUCE node12 172.22.156.12 4444
    def handleMessage(self, message, addr):

        bytes = len(message)

        print("\thandleMessage: " + str(message))
        message = message.split()

        ip, port = message[0].split(":")
        ip = str(ip)
        port = int(port)

        message2send = message[1:]

        if((ip,port) not in self.receivedMessagesByAddress.keys()):
            self.receivedMessagesByAddress[(ip,port)] = [message2send]
        else:
            self.receivedMessagesByAddress[(ip, port)] += [message2send]

        if ("TRANSACTION" in message2send):
            #print("~~got transaction from " +str(addr) + " ~~")

            if(message2send not in self.transactionMessages):
                self.transactionMessages.append(message2send)

            replyMessage = str(self.ip)+":"+str(self.port) + " REPLY"
            print("~~ sending REPLY ~~")
            print("\t" + str(replyMessage))
            self.sock.sendto(replyMessage.encode('utf-8'), (ip, int(port)))
            self.liveAddresses.append((ip,int(port)))

            logMessage = message2send[:]
            print(logMessage)
            # timestamp = logMessage[1]
            # txID = logMessage[2]
            #
            # fromNode = self.service_ip
            # toNode = self.ip
            # sentTime = time.time()
            # status = "alive"
            # nodeNum = self.vmNumber
            # mess = str(" ".join(logMessage))
            #
            # fileString = " " + str(timestamp) + " " + str(type) + " " + str(txID) + " " + str(mess) + " " + str(
            #     fromNode) + " " + str(toNode) + " " + str(sentTime) + " " + str(status) + " " + str(
            #     nodeNum) + " " + str(bytes) + "\n"
            # logging.debug(fileString)

        # Assume you will only get good messages
        elif ("INTRODUCE" in message2send):
            self.introductionMessages.append(message)


        elif ("REPLY" in message2send):
            #print("~~ got reply from " + str(addr) + "~~")
            if((ip, port) in self.pendingAddresses.keys()):
                del self.pendingAddresses[(ip,port)]
                self.liveAddresses.append((ip, port))



##################################
    def serviceRead(self):
        messageFromService = self.serv.readFromService()
        if (messageFromService is not None):
            messagesFromService = messageFromService.split("\n")
            for mess in messagesFromService:
                stripped = messageFromService.strip()
                #print(str(self.name) + ":" + str(stripped))
                #self.file.write(mess)
            return messagesFromService
        return None

    def handleServiceMessage(self, message):

        bytes = len(message)

        message = message.split(" ")

        logMessage = message[:]
        timestamp = message[1]
        txID = message[2]
        mess = str(" ".join(logMessage))
        fromNode = self.service_ip
        toNode = self.ip
        sentTime = time.time()
        status = "alive"
        nodeNum = self.vmNumber

        type = None
        if ("TRANSACTION" in message):

            type = "TRANSACTION"

            #print("~~got transaction from service~~")
            #print("\t" + str(message))
            # Assume it hasn't been seen
            self.transactionMessages.append(message)
            # for tm in self.transactionMessages:
            #     print(tm)

        elif ("INTRODUCE" in message):

            type = "INTRODUCE"

            #print("~~got introduction~~")
            #print("\t" + str(message))
            self.serviceIntroductionMessages.append(message)


        elif ("QUIT" in message):
            #print("## Got Quit command ##")
            type = "QUIT"


        elif ("DIE" in message):
            exit(1)
            #print("@@ Got DIE command @@")

        fileString = " " + str(timestamp) + " " + str(type) + " " + str(txID) + " " + str(mess) + " " + str(
            fromNode) + " " + str(toNode) + " " + str(sentTime) + " " + str(status) + " " + str(
            nodeNum) + " " + str(bytes) + "\n"
        logging.debug(fileString)

        if(type == "QUIT"):
            self.shutdown()


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
            for address, sent_time in self.pendingAddresses.items():
                curr_time = time.time()
                diff = curr_time - sent_time
                # change this to be the timeout factor
                if (diff > 100):
                    print(str(address) + " is dead!")
                    del self.pendingAddresses[address]
                    self.deadAddresses.append(address)

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

                # print("transactionsToSend")
                # for t in transactionsToSend:
                #     print("\t" + str(t))
                # print("readyToSend")
                # for ip in readyToSend:
                #     print("\t" + str(ip))

                ipsToPending = set()

                for transMessage in transactionsToSend:
                    for address in readyToSend:

                        ip, port = address
                        ip = str(ip)
                        port = int(port)

                        message2send = str(self.ip) + ":" + str(self.port) + " " + str(" ".join(transMessage))

                        logMessage = transMessage[:]

                        timestamp = transMessage[1]
                        type = "TRANSACTION"
                        txID = transMessage[2]
                        mess = str(" ".join(logMessage))
                        fromNode = self.ip

                        # Haven't sent them anything yet
                        if((ip, port) not in self.sentMessagesByAddress.keys()):
                            # Have received messages
                            if ((ip, port) in self.receivedMessagesByAddress.keys()):
                                # Haven't received this specific message
                                if (transMessage not in self.receivedMessagesByAddress[(ip, port)]):
                                    print("!! " + str(transMessage) + " > " + str(address) + " !!")

                                    ######### SENDING SECTION #######
                                    self.sock.sendto(message2send.encode('utf-8'), (ip, port))

                                    ### LOGGING STUFF ###
                                    toNode = ip
                                    sentTime = time.time()
                                    status = "alive"
                                    nodeNum = self.vmNumber
                                    bytes = len(message2send)
                                    fileString = " "+str(timestamp)+" "+str(type)+ " "+str(txID)+" "+str(mess)+" "+str(fromNode)+" "+str(toNode)+" "+str(sentTime)+" "+str(status)+" "+str(nodeNum)+" "+str(bytes)+"\n"
                                    logging.debug(fileString)

                                    self.sentMessagesByAddress[(ip, port)] = [transMessage]
                                    ipsToPending.add((ip,port))


                            # Haven't received anything
                            else:
                                print("!! " + str(transMessage) + " > " + str(address) + " !!")

                                ######### SENDING SECTION #######
                                self.sock.sendto(message2send.encode('utf-8'), (ip, port))
                                self.sentMessagesByAddress[(ip, port)] = [transMessage]
                                ipsToPending.add((ip, port))
                        # Have sent them something
                        else:
                            # Message hasn't been sent
                            if (transMessage not in self.sentMessagesByAddress[(ip, port)]):
                                # Message didn't come from them
                                if(transMessage not in self.receivedMessagesByAddress[(ip,port)]):
                                    print("!! " + str(transMessage) + " > " + str(address) + " !!")

                                    ######### SENDING SECTION #######
                                    self.sock.sendto(message2send.encode('utf-8'), (ip, port))
                                    self.sentMessagesByAddress[(ip, port)] += [transMessage]
                                    ipsToPending.add((ip, port))

                # only remove stuff if it was sent
                for ipPort in ipsToPending:
                    if(ipPort in self.liveAddresses):
                        self.liveAddresses.remove(ipPort)
                        self.pendingAddresses[ipPort] = time.time()
                    if (ipPort in self.unknownAddresses):
                        self.unknownAddresses.remove(ipPort)
                        self.pendingAddresses[ipPort] = time.time()



                readyToSend = []
                transactionsToSend = []

            ## IDK WHY THIS IS NECESSARY
            ## RUN EVENT IS NOT PROPERLY CHECKED OTHERWISE
            #time.sleep(1)
            time.sleep(0.001)


        print("Run event unset!")
        print(str(self.vmNumber) + ": Final List")
        time.sleep(self.vmNumber)
        for tm in self.transactionMessages:
            print(tm)
        self.shutdown()






