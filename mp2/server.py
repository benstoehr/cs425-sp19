
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
        self.sock = socket.socket()
        self.hostname = socket.gethostname()
        self.ip = socket.gethostbyname(self.hostname)

        print("hostname: " + str(self.hostname))

        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.settimeout(0.5)

        self.sock.bind((self.hostname, MY_PORT))
        self.sock.listen(10)

    def acceptConnection(self):

        connection = None
        ip_and_port = None

        try:
            self.sock.settimeout(0.25)
            connection, (ip, port) = self.sock.accept()
            print("Accepted connection from: " +str(ip))

            if (connection is not None):
                if (ip in self.connections.items()):
                    connection.send("ALREADYCONNECTED\n".encode('utf-8'))
                    connection.close()
                else:
                    connection.send("FRESHCONNECTION\n".encode('utf-8'))
                    # ip_and_port -> (connection, port, number_of_reads, number_received_messages, messages)
                    self.connections[ip] = (connection, port, 0, 0, [])

        except socket.error as error_msg:
            self.acceptAttempts += 1
            #print(error_msg)

        return connection, ip_and_port

    def connect2Service(self):

        try:
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

    def readFromService(self):

        try:
            self.serviceReadAttempts += 1
            message = (self.serviceSocket.recv(1024)).decode('utf-8')

            print(str(self.name) + ": " + str(self.serviceMessageCount) + ": " + str(message))

            self.serviceMessageCount += 1

            splitMessage = message.strip("\n").split(" ")
            print(splitMessage)

            if (splitMessage[0] == "TRANSACTION"):
                self.transactionMessages.append(message)
            elif (splitMessage[0] == "INTRODUCE"):
                self.introductionMessages.append(message)

        # timeout, keep going
        except socket.error as error_msg:
            # print(error_msg)
            # print("recv timeout")
            pass

    def connectToNewNodes(self):

        for introduction in self.introductionMessages:
            ip = introduction.strip().split(" ")[2]
            port = introduction.strip().split(" ")[3]
            if(ip not in self.connections.keys()):
                self.connect2Node(ip,port)

    def connect2Node(self, ip, port):

        try:
            nu_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            nu_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

            if(ip not in self.connections.keys()):
                connectionCheck = nu_socket.connect((ip, port))
                if(connectionCheck == -1):
                    print("connectionCheck: " + str(-1))

                nu_socket.setblocking(0)
                self.connections[ip] = (nu_socket, port, 0, 0, [])

        except socket.error as error_msg:
            print(error_msg)

    def readFromNodes(self):

        for ip, (connection, port, num_reads, num_messages_read, num_sends, messages) in self.connections.items():

            # try to read from node
            try:
                num_reads += 1
                message = str(connection.recv(1024))
                num_messages += 1
                print(str(self.name) + ": " + str(num_reads) + ": " + str(message))

                splitMessage = message.strip().split(" ")
                print(splitMessage)

                if (splitMessage[0] == "TRANSACTION"):
                    if(message not in self.transactionMessages):
                        self.transactionMessages.append(message)
                elif (splitMessage[0] == "INTRODUCE"):
                    if(message not in self.introductionMessages):
                        self.introductionMessages.append(message)

            except socket.error as error_msg:
                print(error_msg)

    def sendToNodes(self, last5Messages):

        for ip, (connection, port, num_reads, num_messages_read, num_sends, messages) in self.connections.items():

            for message in last5Messages:
                try:
                    bytes_sent = connection.send(message.encode('utf-8'))
                    num_sends += 1
                except socket.error as error_msg:
                    print(error_msg)

    def shutdown(self):
        #print("Server: shutdown")
        for connection, ip_and_port in self.connections.items():
            print("Closing connections!")
            connection.close()

    def lastX(self, num):
        for message in self.transactionMessages[:-5]:
            print(message)

        return self.transactionMessages[:-5].copy()

    def printConnections(self):
        for ip, (connection, port, num_reads, num_messages_read, num_sends, messages) in self.connections.items():
            try:
                if(connection.is_alive()):
                    print(str(connection) + ":" + str(port))
            except socket.error as error_msg:
                print(error_msg)

    def printMessages(self):
        print("TRANSACTIONS")
        for transaction in self.transactionMessages:
            print("\t" + str(transaction))
        print("INTRODUCTIONS")
        for introduction in self.introductionMessages:
            print("\t" + str(introduction))

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

        messageCount = 0

##### MAIN LOOP #######

        while(self.event.is_set()):

            # Listen for incoming connections
            self.acceptConnection()

            # try to read from service
            self.readFromService()

            # try to read from nodes
            self.readFromNodes()

            self.connectToNewNodes()

            # send last 5 transactions
            last5 = self.lastX(5)

            self.sendToNodes(last5)

            time.sleep(0.1)

            self.printConnections()
            self.printMessages()

        print("Server: unset")
        #self.shutdown()



















