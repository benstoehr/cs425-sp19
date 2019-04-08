
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
from logger import Logger

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
    introductionMessages_Handled = []


    serviceIntroductionMessages = []
    serviceTransactionMessages = []

    replyMessages = []

    nameIPPortList = []
    ipAndport2Name = dict()

    # (ip,(int) port) IMPORTANT
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
        print("logfile: " +str(filename))
        #self.file = open(filename, "w+")

        logging.basicConfig(filename="log.txt", format=self.name+' - %(message)s', level=logging.DEBUG)
        self.logger = Logger(logging, self.ip, self.port, self.vmNumber)
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

###
    def replyAndUpdateAddresses(self, ip, port):
        # REPLY
        self.sendReply(ip, port)
        # KEEP THIS ADDRESS AS ALIVE
        self.liveAddresses.append((ip, int(port)))

    def sendReply(self, ip, port):
        replyMessage = str(self.ip) + ":" + str(self.port) + " REPLY"
        print("~~ sending REPLY ~~")
        print("\t" + str(replyMessage))
        self.sock.sendto(replyMessage.encode('utf-8'), (ip, int(port)))



    def clearIPPortFromAddresses(self, ip, port):
        for introMessage in self.introductionMessages_Handled:
            if(ip in introMessage and port in introMessage):
                self.introductionMessages_Handled.remove(introMessage)

    def getAddressesToSend(self):
        # Shuffle the live addresses
        random.shuffle(self.liveAddresses)

        readyToSend = None
        readyToSendLive = None
        readyToSendUnknown = None

        # from live addresses
        if (len(self.liveAddresses) < 3):
            readyToSendLive = self.liveAddresses
        else:
            readyToSendLive = self.liveAddresses[:3]

        # from unknown addresses
        if (len(self.unknownAddresses) < 2):
            readyToSendUnknown = self.unknownAddresses
        else:
            readyToSendUnknown = self.unknownAddresses[:2]

        readyToSend = readyToSendLive + readyToSendUnknown
        return readyToSend

    def okToSend(self, ip, port, message):

        # Haven't sent them anything yet
        if ((ip, port) not in self.sentMessagesByAddress.keys()):
            self.sentMessagesByAddress[(ip, port)] = []

        if ((ip, port) not in self.receivedMessagesByAddress.keys()):
            self.receivedMessagesByAddress[(ip, port)] = []

        # Haven't sent or received this message from this ip, port
        if (message not in self.sentMessagesByAddress[(ip, port)]):
            if (message not in self.receivedMessagesByAddress[(ip, port)]):
                return True

        return False

    def addMessagetoSentMessages(self, ip, port, message):
        # Haven't sent them anything yet
        if ((ip, port) not in self.sentMessagesByAddress.keys()):
            self.sentMessagesByAddress[(ip, port)] = [message]
        else:
            self.sentMessagesByAddress[(ip, port)] += [message]

    def storeMessage(self, ip, port, message):
        if ((ip, port) not in self.receivedMessagesByAddress.keys()):
            self.receivedMessagesByAddress[(ip, port)] = [message]
        else:
            self.receivedMessagesByAddress[(ip, port)] += [message]

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
        # RETURNS MESSAGE AS A STRING, ADDR AS (IP, PORT), DOESN'T MATTER THO BECAUSE THE IP AND PORT ARE IN THE MESSAGE
        return message, addr

    # TRANSACTION 1551208414.204385 f78480653bf33e3fd700ee8fae89d53064c8dfa6 183 99 10
    # INTRODUCE node12 172.22.156.12 4444
    def handleMessage(self, message, addr):

        print("\thandleMessage: " + str(message))

        # message = IP:Port messageContents[]
        message = message.split()
        ip, port = message[0].split(":")
        ip = str(ip)
        port = int(port)
        message2send = message[1:]

        if ("TRANSACTION" in message2send):
            #print("~~got transaction from " +str(addr) + " ~~")
            self.logger.logReceivedTransaction(' '.join(message))
            # IF YOU HAVEN'T SEEN THIS TRANSACTION, SAVE IT!
            if(message2send not in self.transactionMessages):
                self.transactionMessages.append(message2send)

            self.storeMessage(ip, port, message2send)
            self.replyAndUpdateAddresses(ip, port)

        elif ("INTRODUCE" in message2send):
            self.logger.logReceivedIntroduction(' '.join(message))
            if(message2send not in self.introductionMessages):
                self.introductionMessages.append(message2send)

            self.storeMessage(ip, port, message2send)
            self.replyAndUpdateAddresses(ip, port)

        elif ("REPLY" in message2send):
            #print("~~ got reply from " + str(addr) + "~~")
            if((ip, port) in self.pendingAddresses.keys()):
                del self.pendingAddresses[(ip,port)]
                self.liveAddresses.append((ip, port))



##################################

    # READ FROM THE SERVICE
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


    # HANDLE THE SERVICE MESSAGE, MESSAGE COMES IN AS A STRING
    def handleServiceMessage(self, message):

        # Print the message to console
        print("handleServiceMessage: " +str(message))
        bytes = len(message)

        # MESSAGE IS NOW AN ARRAY
        message = message.split(" ")

        logMessage = message[:]

        mess = str("_".join(logMessage))
        fromNode = str(self.service_ip) + str(self.service_port)
        toNode = str(self.ip) + str(self.port)
        sentTime = time.time()
        status = "alive"
        nodeNum = self.vmNumber
        ttype = None
        timestamp_a = None
        txID = None

        if ("TRANSACTION" in message):
            #print("~~got transaction from service~~")
            #print("\t" + str(message))
            # Assume it hasn't been seen
            self.logger.logServiceTransaction(self.service_ip, self.service_port, message)
            self.transactionMessages.append(message)

        elif("INTRODUCE" in message):
            #print("~~got introduction~~")
            #print("\t" + str(message))
            self.logger.logServiceIntroduction(self.service_ip, self.service_port, message)
            self.serviceIntroductionMessages.append(message)
            self.introductionMessages.append(message)


        elif ("QUIT" in message):
            #print("## Got Quit command ##")
            ttype = "QUIT"

        elif ("DIE" in message):
            self.status = "shutdown"
            time.sleep(0.05)
            exit(1)
            #print("@@ Got DIE command @@")

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


    ############### STEP 1: READ ALL MESSAGES ###################
        ## 1.A -- READ ALL MESSAGES FROM SERVICE
            ## Read until no messages
            while(1):
                #print("serviceRead()")
                serviceMessages = self.serviceRead()
                if(serviceMessages is None):
                    # NOTHING TO READ MOVE ON
                    break
                for serviceMessage in serviceMessages:
                    serviceMessageType = self.messager.getMessageType(serviceMessage)
                    # FOR EVERY GOOD MESSAGE, HANDLE IT
                    if(serviceMessageType is not None):
                        self.handleServiceMessage(serviceMessage)

            ######## Update list of IPs from node messages
            # serviceIntroMessage = ['INTRODUCE', 'node2', '172.22.156.3', '4567']
            for serviceIntroMessage in self.serviceIntroductionMessages:
                print("Converting message to dictionary entry and adding to liveAddresses")
                vmname = serviceIntroMessage[1]
                vmIP = serviceIntroMessage[2]
                vmPort = int(serviceIntroMessage[3])
                if((vmIP, vmPort) not in self.ipAndport2Name.keys()):
                    # Put it in the dictionary with the name
                    self.ipAndport2Name[(vmIP, vmPort)] = (vmname, "alive")
                    # put it in the list of live addresses
                    self.liveAddresses.append((vmIP, vmPort))
            # EMPTY THE QUEUE
            self.serviceIntroductionMessages = []

        ## 1.B -- READ ALL MESSAGES FROM NODES
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
                vmPort = int(introMessage[3])
                if((vmIP, vmPort) not in self.ipAndport2Name.keys()):
                    # Put it in the dictionary with the name
                    self.ipAndport2Name[(vmIP, vmPort)] = (vmname, "unknown")
                    self.unknownAddresses.append((vmIP, vmPort))
                # Move the message to a "HANDLED" array
                self.introductionMessages_Handled.append(introMessage)
            self.introductionMessages = []

    ## END OF READING ##########

        ## 2.A -- ADDRESS CLEAN UP
            ## Delete addresses that are stale
            for address, sent_time in self.pendingAddresses.items():
                curr_time = time.time()
                diff = curr_time - sent_time
                # change this to be the timeout factor
                if (diff > 100):
                    print(str(address) + " is dead!")
                    del self.pendingAddresses[address]
                    vmname, status = self.ipAndport2Name[address]
                    self.ipAndport2Name[address] = (vmname, "dead")
                    self.deadAddresses.append(address)
                    self.clearIPPortFromAddresses(ip, port)

    ## Figure out which addresses to send to

            addresses = self.getAddressesToSend()

            ## Sort the transactions
            sortedTranscations = sorted(self.transactionMessages, key=sortFunction)
            transactionsToSend = None
            if (len(sortedTranscations) < 5):
                transactionsToSend = sortedTranscations
            else:
                transactionsToSend = sortedTranscations[-5:]


            random.shuffle(self.introductionMessages_Handled)
            introductionsToSend = None
            if (len(self.introductionMessages_Handled) < 3):
                introductionsToSend = self.introductionMessages_Handled
            else:
                introductionsToSend = self.introductionMessages_Handled[-3:]


            ######## WRITE TO OTHER NODES ######
            ipsToPending = set()

            if(len(transactionsToSend) > 0 and len(addresses) > 0):

                for address in addresses:

                    ip, port = address
                    ip = str(ip)
                    port = int(port)

                    # TRANSACTIONS
                    for transMessage in transactionsToSend:
                        message2send = str(self.ip) + ":" + str(self.port) + " " + str(" ".join(transMessage))

                        if(self.okToSend(ip, port, transMessage)):
                            print("!! " + str(message2send) + " > " + str(address) + " !!")
                            ######### SENDING SECTION #######
                            self.sock.sendto(message2send.encode('utf-8'), (ip, port))
                            self.logger.logSentTransaction(ip, port, message2send)
                            self.addMessagetoSentMessages(ip, port, transMessage)
                            ipsToPending.add((ip, port))

                    ## INTRODUCTIONS
                    if(introductionsToSend is not None):
                        for intro in introductionsToSend:
                            message2send = str(self.ip) + ":" + str(self.port) + " " + str(" ".join(intro))

                            if (self.okToSend(ip, port, intro)):
                                print("!! " + str(message2send) + " > " + str(address) + " !!")
                                ######### SENDING SECTION #######
                                self.sock.sendto(message2send.encode('utf-8'), (ip, port))
                                self.logger.logSentIntroduction(ip, port, message2send)
                                self.addMessagetoSentMessages(ip, port, intro)
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






