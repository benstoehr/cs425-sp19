## import socketserver as ss
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


def sortFunction(x):
    return x[1]

class mp2Server(object):

    status = None

    hostname = None
    ip = None
    port = None
    name = None

    sock = None
    service_ip = None
    service_port = None

    serviceSocket = None

    connections = dict()

    acceptAttempts = 0

    serviceReadAttempts = 0
    serviceMessageCount = 0

    transactionMessages = []
    introductionMessages = []


    def __init__(self, SERVICE_IP, SERVICE_PORT, NAME, MY_PORT, EVENT):
        #Thread.__init__(self)

        self.service_ip = SERVICE_IP
        self.service_port = int(SERVICE_PORT)
        self.name = NAME
        self.port = int(MY_PORT)
        self.event = EVENT

        self.status = "Initializing"
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.hostname = socket.gethostname()
        self.ip = socket.gethostbyname(self.hostname)

        print("hostname: " + str(self.hostname))

        #self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        #self.sock.settimeout(0.5)

        self.sock.bind((self.hostname, MY_PORT))

    def connect2Service(self):

        try:
            # Setup TCP socket
            self.serviceSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.serviceSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            print("self.service_ip: " + str(self.service_ip))

            connectionCheck = self.serviceSocket.connect((self.service_ip, self.service_port))
            if(connectionCheck == -1):
                print("connectionCheck: " + str(-1))
            self.serviceSocket.setblocking(0)
            self.service = self.serviceSocket.getpeername()
            print("Service name: " + str(self.service))

        except socket.error as error_msg:
            print(error_msg)




    def openSocket(self):
        # Setup TCP socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        #self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.ip, self.port))
        self.sock.settimeout(0.25)

################################
    def shutdown(self):
        self.serviceSocket.send(("").encode('utf-8'))
        self.serviceSocket.close()
        self.sock.close()

    def lastX(self, num):
        for message in self.transactionMessages[:-5]:
            print(message)

        return self.transactionMessages[:-5].copy()

    def printConnections(self):
        for ip, (connection, port, num_reads, num_messages_read, num_sends, messages) in self.connections.items():
            if(connection is not None):
                print(str(ip) + ":" + str(port))

    def printMessages(self):

        if(len(self.transactionMessages) > 0):
            print("TRANSACTIONS")
            for transaction in self.transactionMessages:
                print("\t" + str(transaction.strip("\n")))

        if (len(self.introductionMessages) > 0):
            print("INTRODUCTIONS")
            for introduction in self.introductionMessages:
                print("\t" + str(introduction))


################################

    def start(self):

        self.connect2Service()

        str2Send = ""
        str2Send += "CONNECT "
        str2Send += self.name
        str2Send += " "
        str2Send += self.ip
        str2Send += " "
        str2Send += str(self.port)
        str2Send += "\n"

        print("str2Send: " + str(str2Send))

        try:
            self.serviceSocket.send(str2Send.encode('utf-8'))
            #firstMessageLength = self.serviceSocket.recv(1024)
            #print("firstMessage: " +str(firstMessageLength))
        except socket.error as error_msg:
            #self.serviceSocket = None
            print("Error connection to service!")

        print("Done reading from service!")

    def readFromService(self):
        try:
            self.serviceReadAttempts += 1
            message = (self.serviceSocket.recv(1024)).decode('utf-8')
            #print(str(self.name) + ": " + str(self.serviceMessageCount) + ": " + str(message))
            self.serviceMessageCount += 1

        # timeout, keep going
        except socket.error as error_msg:
            # print(error_msg)
            #print("No message from Service")
            return "0"

        return message

    def read(self):

        try:
            messageFromService = self.serviceSocket.recv(1024)
            message, addr = self.sock.recvfrom(1024)
            # firstMessageLength = self.serviceSocket.recv(1024)
            # print("firstMessage: " +str(firstMessageLength))
        except socket.error as error_msg:
            # self.serviceSocket = None
            #print("No message to receive!")
            return "0"

        return message



















