
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

from block import Block
from BlockManager import BlockManager


def sortFunction(x):
    return x[1]


class Node(Thread):

    #global run_event


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

    sentAddressesByBlock = dict()
    receivedAddressesByBlock = dict()




    def __init__(self, SERVICE_IP, SERVICE_PORT, name, MY_PORT, event):
        Thread.__init__(self)

        # Socket to send stuff
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # self identification
        self.status = "Initializing"
        self.host = socket.gethostname()
        print("self.host: " + str(self.host))
        self.name = name
        print("name: " +str(self.name))
        self.vmNumber = int(self.name[8])
        # Networking
        self.ip = socket.gethostbyname(self.host)
        print("self.ip:" + str(self.ip))
        self.port = MY_PORT
        self.service_ip = SERVICE_IP
        self.service_port = SERVICE_PORT

        # server
        self.serv = None

        self.event = event

        logging.basicConfig(filename="log.txt", format='%(message)s', level=logging.DEBUG)
        self.logger = Logger(logging, self.ip, self.port, self.vmNumber, self.name)
        self.messager = Messager()

        ## CP2
        self.blockManager = BlockManager()

        self.ipsToSendChain = []

        # Should only ever be a string with a hash
        self.hashesSentToService = []



    # TODO:
    # Initialize server
    # Params: port

    def initServer(self):
        self.serv = mp2Server(self.service_ip, self.service_port, self.name, self.port, self.event)

    def startServer(self):
        self.serv.start()

    def closeServiceConnection(self):
        self.serv.shutdown()

    def shutdown(self):

        print(str(self.name) + " shutting down")

        #self.file.close()
        print(str(self.name) + " Exiting")
        self.status = "shutdown"

############
    def replyAndUpdateAddresses(self, ip, port):
        # REPLY
        self.sendReply(ip, port)
        # KEEP THIS ADDRESS AS ALIVE
        self.liveAddresses.append((ip, int(port)))

    def sendReply(self, ip, port):
        replyMessage = str(self.ip) + ":" + str(self.port) + " REPLY"
        #print("~~ sending REPLY ~~")
        #print("\t" + str(replyMessage))
        self.sock.sendto(replyMessage.encode('utf-8'), (ip, int(port)))

    def requestChain(self, ip, port):
        requestChainMessage = str(self.ip) + ":" + str(self.port) + " REQUESTCHAIN" + "\n"
        self.sock.sendto(requestChainMessage.encode('utf-8'), (ip, int(port)))

##############
    def clearIPPortFromAddresses(self, address):
        ip, port = address
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

    def addMessagetoReceivedMessages(self, ip, port, message):
        if ((ip, port) not in self.receivedMessagesByAddress.keys()):
            self.receivedMessagesByAddress[(ip, port)] = [message]
        else:
            self.receivedMessagesByAddress[(ip, port)] += [message]

    def okToSendBlock(self, blockString, ip, port):
        if(blockString not in self.sentAddressesByBlock.keys()):
            self.sentAddressesByBlock[blockString] = [(self.ip, self.port)]

        if(blockString not in self.receivedAddressesByBlock.keys()):
            self.receivedAddressesByBlock[blockString] = [(self.ip, self.port)]

        if((ip,int(port)) not in self.sentAddressesByBlock[blockString]):
            if((ip, int(port)) not in self.receivedAddressesByBlock[blockString]):
                return True
        return False

    def addAddresstoSentBlocks(self, block, ip, port):
        if ((ip, port) not in self.sentAddressesByBlock.keys()):
            self.sentAddressesByBlock[block] = [(ip, int(port))]
        else:
            self.sentAddressesByBlock[block] += [(ip, int(port))]

    def addAddresstoReceivedBlocks(self, block, ip, port):
        if ((ip, port) not in self.receivedAddressesByBlock.keys()):
            self.receivedAddressesByBlock[block] = [(ip, int(port))]
        else:
            self.receivedAddressesByBlock[block] += [(ip, int(port))]


#### List manipulation
    def getNameAndPortFromIP(self):
        pass

###### READING FUNCTIONS

    def read(self):
        message, addr = self.serv.read()
        #print("read() -> got message, addr")
        if (message is not None):
            #print("Got message in read() call!")
            stripped = message.strip()
            #print(str(self.name) + ": " + str(stripped))
        # RETURNS MESSAGE AS A STRING, ADDR AS (IP, PORT), DOESN'T MATTER THO BECAUSE THE IP AND PORT ARE IN THE MESSAGE
        return message, addr

    # TRANSACTION 1551208414.204385 f78480653bf33e3fd700ee8fae89d53064c8dfa6 183 99 10
    # INTRODUCE node12 172.22.156.12 4444
    def handleMessage(self, message, addr):

        #print("\thandleMessage: " + str(message))

        # message = IP:Port messageContents[]
        message = message.split()
        ip, port = message[0].split(":")
        ip = str(ip)
        port = int(port)
        message2send = message[1:]

        ## CP 1
        if ("TRANSACTION" in message2send):
            #print("~~got transaction from " +str(addr) + " ~~")
            self.logger.logReceivedTransaction(' '.join(message))
            # IF YOU HAVEN'T SEEN THIS TRANSACTION, SAVE IT!
            if(message2send not in self.transactionMessages):
                self.transactionMessages.append(message2send)
                ## ADD IT TO THE BLOCK MANAGER
                hash = self.blockManager.appendTransactionToCurrentBlock(message2send)

            self.addMessagetoReceivedMessages(ip, port, message2send)
            self.replyAndUpdateAddresses(ip, port)

        elif ("INTRODUCE" in message2send):
            self.logger.logReceivedIntroduction(' '.join(message))
            if(message2send not in self.introductionMessages):
                self.introductionMessages.append(message2send)

            self.addMessagetoReceivedMessages(ip, port, message2send)
            self.replyAndUpdateAddresses(ip, port)

        elif ("REPLY" in message2send):
            #print("~~ got reply from " + str(addr) + "~~")
            if((ip, port) in self.pendingAddresses.keys()):
                del self.pendingAddresses[(ip,port)]
                self.liveAddresses.append((ip, port))

        # CP 2
        elif("BLOCK" in message2send):
            print("Received block from " + str(ip) + " " +str(port))
            print(message2send)

            #self.logger.logReceivedBlock(' '.join(message)

            #blockWord, blockString = message2send
            self.addAddresstoReceivedBlocks(' '.join(message2send), ip, port)

            # if level is greater, you have to ask for the whole blockchain

            if(self.blockManager.betterBlock(ip, port, message2send)):
                print("NODE CALLED BETTER BLOCK AND IT WAS TRUE")
                self.requestChain(ip, port)
                print("Waiting for chain from: " + str(self.blockManager.waitingForBlockChainFrom))
                #self.blockManager.updateBlock()
                #self.currentBlockString = message2send

            # if level is the same, do nothing
            else:
                pass

        elif("BLOCKCHAIN" in message2send):
            # Pass on individual block to build chain
            print("Building new chain with block")
            print(message)
            if(self.blockManager.waitingForBlockChainFrom == (ip, port)):
                self.blockManager.buildChain(message2send)
                pass

        elif("REQUESTCHAIN" in message2send):
            print("Full CHAIN requested from " + str(ip) + "," + str(port))
            self.ipsToSendChain += [(ip, port)]


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
        #print("handleServiceMessage: " +str(message))
        bytes = len(message)

        # MESSAGE IS NOW AN ARRAY
        message = message.split(" ")

        if ("TRANSACTION" in message):
            #print("~~got transaction from service~~")
            #print("\t\t" + str(message))
            # Assume it hasn't been seen
            self.logger.logServiceTransaction(self.service_ip, self.service_port, message)
            self.transactionMessages.append(message)

            ## ADD IT TO THE BLOCK MANAGER
            self.blockManager.appendTransactionToCurrentBlock(message)

        elif("INTRODUCE" in message):
            #print("~~got introduction~~")
            #print("\t" + str(message))
            self.logger.logServiceIntroduction(self.service_ip, self.service_port, message)
            self.serviceIntroductionMessages.append(message)
            self.introductionMessages.append(message)

        elif("SOLVED" in message):
            print("\n~~ got Solved ~~")
            #print(message)
            print(str(message[1]))
            print(str(message[2]))
            if(self.blockManager.successfulBlock(message)):
                self.currentBlockString = self.blockManager.currentBlockAsString()
                self.blockManager.newBlock()
                ## make all of the pending transactions go into new block
                self.blockManager.fillNewBlock()
            else:
                print("Ignoring SOLVED Message")

            print("\n\t\t\t\t\t\t\t\t\t\t\t\t\t[RECEIVING]")

        elif("VERIFY OK" in message):
            print("~~ got Good Verify ~~")
            print("\t" + str(message))
            pass

        elif("VERIFY FAIL" in message):
            print("~~ got Bad Verify ~~")
            print("\t" + str(message))
            pass

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

        # Check if ctrl + C was pressed
        while (1):
            if(self.event.isSet()):
                self.closeServiceConnection()
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
                    self.clearIPPortFromAddresses(address)

    ## 3.A -- Figure out which addresses to send to

            addresses = self.getAddressesToSend()
    ## 3.B -- Figure out transactions to send

            ## Sort the transactions
            sortedTranscations = sorted(self.transactionMessages, key=sortFunction)
            transactionsToSend = None
            if (len(sortedTranscations) < 5):
                transactionsToSend = sortedTranscations
            else:
                transactionsToSend = sortedTranscations[-5:]

    ## 3.C -- Figure out which random introductions to send

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
            ## 4.A
                    # TRANSACTIONS
                    for transMessage in transactionsToSend:
                        message2send = str(self.ip) + ":" + str(self.port) + " " + str(" ".join(transMessage))
                        if(self.okToSend(ip, port, transMessage)):
                            #print("!! " + str(message2send) + " > " + str(address) + " !!")
                            ######### SENDING SECTION #######
                            self.sock.sendto(message2send.encode('utf-8'), (ip, port))
                            self.logger.logSentTransaction(ip, port, message2send)
                            self.addMessagetoSentMessages(ip, port, transMessage)
                            ipsToPending.add((ip, port))
            ## 4.B
                    ## INTRODUCTIONS
                    if(introductionsToSend is not None):
                        for intro in introductionsToSend:
                            message2send = str(self.ip) + ":" + str(self.port) + " " + str(" ".join(intro))
                            if (self.okToSend(ip, port, intro)):
                                #print("!! " + str(message2send) + " > " + str(address) + " !!")
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

            ## CP2 #########################

            ## SENDING NEWEST HASH FOR SOLVING
            if(self.blockManager.currentBlock is not None):
                if(self.blockManager.currentBlock.selfHash is not None):
                    if(self.blockManager.currentBlock.selfHash not in self.hashesSentToService):
                        self.hashesSentToService.append(self.blockManager.currentBlock.selfHash)
                        print("SOLVE:")
                        self.blockManager.printCurrentBlock()
                        string = "SOLVE "
                        string += self.blockManager.currentBlock.selfHash
                        string += "\n"
                        print("\n\t\t\t\t\t\t\t\t\t\t\t\t\t[RECEIVING]")
                        self.serv.serviceSocket.send(string.encode('utf-8'))

            ## SENDING BLOCK TO OTHER NODES
            if(not self.blockManager.waitingForBlockChain and self.blockManager.lastSuccessfulHash is not None):

                blockString = self.blockManager.lastSuccessfulBlock.toMessageWithHash()
                blockMessage2send = str(self.ip) + ":" + str(self.port) + " " + str(blockString)
                for address in addresses:
                    ip, port = address
                    ip = str(ip)
                    port = int(port)
                    if(self.okToSendBlock(blockString, ip, port)):
                        print("GONNA SEND MY BLOCK TO NODE: " + str(ip) + "," + str(port))
                        self.blockManager.lastSuccessfulBlock.printSelf()
                        print("")
                        self.sock.sendto(blockMessage2send, (ip, port))
                        self.addAddresstoSentBlocks(blockString, ip, port)


                for ip, port in self.ipsToSendChain:
                    for blockHash, block in self.blockManager.blockchain.values():
                        print("GONNA SEND CHAIN NODE TO: " + str(ip) + "," + str(port))
                        blockString = block.toChainMessage()
                        blockChainMessage2send = str(self.ip) + ":" + str(self.port) + " " + str(blockString)
                        self.sock.sendto(blockChainMessage2send, (ip, port))
                        self.addAddresstoSentBlocks(blockString, ip, port)
                self.ipsToSendChain = []

            ## IDK WHY THIS IS NECESSARY
            ## RUN EVENT IS NOT PROPERLY CHECKED OTHERWISE
            #time.sleep(1)
            time.sleep(0.0000001)


        print("Run event unset!")
        print(str(self.vmNumber) + ": Final List")
        time.sleep(self.vmNumber)
        for tm in self.transactionMessages:
            print(tm)
        print("")

        for i in range(self.blockManager.blockLevel):
            blockHash, block = self.blockManager.blockchain[i+1]
            block.printSelf()
            print("")

        print("\n[PENDING TRANSACTIONS]")
        for pt in self.blockManager.pendingTransactions:
            print(pt)

        print("\nTRANSACTIONS IN CURRENT BLOCK")
        for t in self.blockManager.currentBlock.getTransactions():
            print(t)

        self.shutdown()