import socket
import sys
from threading import Thread
import threading
import time
import logging
import fcntl, os
import errno
import signal

IP_ADDR = ''


# Addresses of other VMs for mp1
VM0 = 'sp19-cs425-g58-01.cs.illinois.edu'
VM1 = 'sp19-cs425-g58-02.cs.illinois.edu'
VM2 = 'sp19-cs425-g58-03.cs.illinois.edu'
VM3 = 'sp19-cs425-g58-04.cs.illinois.edu'
VM4 = 'sp19-cs425-g58-05.cs.illinois.edu'
VM5 = 'sp19-cs425-g58-06.cs.illinois.edu'
VM6 = 'sp19-cs425-g58-07.cs.illinois.edu'
VM7 = 'sp19-cs425-g58-08.cs.illinois.edu'
VM8 = 'sp19-cs425-g58-09.cs.illinois.edu'
VM9 = 'sp19-cs425-g58-10.cs.illinois.edu'
VM_LIST = [VM0, VM1, VM2, VM3, VM4, VM5, VM6, VM7, VM8, VM9]


# takes the first argument from command prompt: user name
NAME = str(sys.argv[1])
# takes the second argument from command prompt:  port number
PORT = int(sys.argv[2])
# takes the third argument from command prompt:  number of users
USER_NUM = int(sys.argv[3])

hostName = socket.gethostname()
#print("hostName: " + str(hostName))

splitHostName = hostName.split("-")
VM_NUMBER = int(splitHostName[3].split(".")[0])
#print("Running on VM: " +  str(VM_NUMBER))

class ServerSocket(Thread):

    def __init__(self, sock=None, num_users=USER_NUM, ip=None, port=None):
        super(ServerSocket, self).__init__()
        if sock is None:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            fcntl.fcntl(self.sock, fcntl.F_SETFL, os.O_NONBLOCK)
        else:
            self.sock = sock

        self.ip = ip
        self.port = port
        self.hostname = socket.gethostname()
        splitHostName = hostName.split("-")
        self.vmNumber = int(splitHostName[3].split(".")[0])

        self.totalUsers = num_users
        self.numberOfClients = num_users - 1

        self.activeInputConnections = 0
        self.activeOutputConnections = 0

        self.vmsNamed = []
        self.connections = dict()

        self.sentMessages = []
        self.messageQueue = []

        self.ready = False

        # # create logger
        # self.logger = logging.getLogger(__name__)
        # self.logger.setLevel(logging.DEBUG)
        # # create console handler and set level to debug
        # ch = logging.StreamHandler()
        # ch.setLevel(logging.INFO)
        # # add ch to logger
        # self.logger.addHandler(ch)

    def bind(self, ip_addr, port):
        bindCheck = self.sock.bind((ip_addr, port))
        listenCheck = self.sock.listen(self.numberOfClients)

    def initializeConnections(self):

        global globalready

        print("\nIP: " +str(self.ip) + "\n")

        self.bind(self.ip, self.port)

        initializeConnectionsStart = time.time()

        while(not self.ready and run_event.is_set()):
            #print("serverWhile")

            currentTime = time.time()
            if(currentTime - initializeConnectionsStart > 20000):
                #self.logger.info("Server: 20 second timeout exceeding when waiting for connections")
                print("Server: 20 second timeout exceeding when waiting for connections")

            if (self.sock is not None):
                # self.logger.info("Server: CALLING ACCEPT()")
                try:
                    print("Accept Call")
                    connection, ip_and_port = self.sock.accept()
                    ip, port = ip_and_port
                    connection.setblocking(0)

                    # self.logger.info('Server: Connection established by: ' + str(ip_address))
                    print('\tIncoming Connection : ' + str(self.sock.getsockname()) + " <- "+ str(ip_and_port))

                    # if the address has been seen, it was seen when trying to connect to other clients
                    if (ip in self.connections.keys()):
                        (hostname, in_connection, out_connection, status, mes2send, sentmes) = self.connections[ip]
                        if(in_connection is not None):
                            print("\tAlready have an incoming connection for " + str(ip))
                            connection.close()
                        else:
                            print("\tNew incoming connection for ip " + str(ip))
                            self.connections[ip] = (hostname, connection, out_connection, 'active', [], [])
                            self.activeInputConnections += 1

                    # Otherwise add connection to connection list
                    else:
                        print("\tNew incoming connection with fresh IP")
                        self.connections[ip] = (None, connection, None, 'active', [], [])
                        self.activeInputConnections += 1

                except socket.error as error:
                    pass
                    print("\tno connections yet")
                    #time.sleep(.5)
                    # print(error)
            else:
                # self.logger.info("Server: self.sock is None in acceptConnections")
                print("Server: self.sock is None in acceptConnections")


            print("VM LIST TIME")
            for vm in VM_LIST:

                if(vm == self.hostname):
                    continue

                new_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                new_connection.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

                try:
                    connectCheck = new_connection.connect((vm, self.port))
                    new_connection.setblocking(0)

                    ip_and_port = new_connection.getpeername()
                    ip, nuport = ip_and_port

                    # already connected to this ip, update the vm hostname
                    if(ip in self.connections.keys()):
                        (hostname, in_connection, out_connection, status, mes2send, sentmes) = self.connections[ip]
                        if(hostname is None and out_connection is None):
                            print("\tOutgoing Connection: " + str(new_connection.getsockname()) + "<->" + str(
                                ip_and_port))
                            print("\tupdating name for " + str(ip) + " to " + str(vm))
                            self.connections[ip] = (vm, in_connection, new_connection, 'active', mes2send, sentmes)
                            self.activeOutputConnections += 1
                            self.vmsNamed += [vm]

                        else:
                            print("\tAlready have outgoing connection to " + str(ip))
                            new_connection.close()

                    else:
                        print("\tOutgoing Connection: " + str(new_connection.getsockname()) + " -> " + str(ip_and_port) + ": " + str(vm))
                        self.connections[ip] = (vm, None, new_connection, 'active',[],[])
                        self.activeOutputConnections += 1
                        self.vmsNamed += [vm]

                except socket.error as e:
                    #print(errno.errorcode[e.errno])
                    #self.connections[server] = (None, 'inactive')
                    new_connection.close()
                    continue

            # Once the proper number of connections is made, exit the while loop
            if(self.activeInputConnections == self.numberOfClients
                    and self.activeOutputConnections == self.numberOfClients
                    and len(self.vmsNamed) == self.numberOfClients):

                self.ready = True
                #self.logger.info("Server: CONNECTED TO ALL THE CLIENTS!")

                print("Server: CONNECTED TO ALL THE CLIENTS!")
                for address, (hostname, in_connection, out_connection, status, mes2send, sentmes) in self.connections.items():
                    print("{}:{}".format(hostname, status))
                    print("IN: " + str(in_connection.getsockname()) + " <-> " + str(in_connection.getpeername()))
                    print("OUT: " + str(out_connection.getsockname()) + " <-> " + str(out_connection.getpeername()) + "\n")

                print("READY")

                c.acquire()
                globalready = True
                #c.notify_all()
                c.release()

            #time.sleep(1)

    def shutdown(self):

        for address, (port, hostname, connection, status, mes2send, sentmes) in self.connections.items():
            if(status == 'active' and connection is not None):
                connection.close()

        self.sock.close()
        exit(1)

    def run(self):

        # make vector global
        global vector
        #global sentMessages
        global clientMessagesToSend

        #print("Server: INSIDE THE RUN FUNCTION")
        self.initializeConnections()

        error_count = 0
        while(run_event.is_set()):

            # TODO: Main server logic
            # iterate over each connection and read 8 bytes for message length

            c.acquire()
            clientMessages = clientMessagesToSend[:]

            for address, (hostname, in_connection, out_connection, status, mes2send, sent_mes) in self.connections.items():
                mes2send_copy = mes2send[:]
                added_messages = mes2send_copy + clientMessages
                self.connections[address] = (hostname, in_connection, out_connection, status, added_messages[:], sent_mes[:])
                clientMessagesToSend = []
            c.release()

            for address, (hostname, in_connection, out_connection, status, mes2send, sent_mes) in self.connections.items():

                if(status == 'active' and out_connection is not None):


                    #print("\tBeginning of Loop mes2send " + str(mes2send))

                    if (len(mes2send) > 0):
                        print("{}: {}".format(hostname, status))
                        print("sending messages from queue " + str(mes2send))
                        print(str(self.hostname) + " -> " + str(hostname) + ": " + str(mes2send))
                        for m in mes2send:
                            # print(m)
                            out_connection.send(m)
                            sent_mes += [m]
                        #mes2send = []

                    try:

                        receiveCheck = in_connection.recv(1)

                        # THIS MEANS THE CONNECTION CLOSED
                        if (len(receiveCheck) == 0):
                            print(str(address) + " disconnected!")
                            in_connection.close()
                            out_connection.close()
                            self.connections[address] = (hostname, None, None, 'inactive', mes2send, sent_mes)
                            break

                        # GET MESSAGE
                        elif (len(receiveCheck) > 0):

                            messageLength = int(ord(receiveCheck)) - 1
                            vmSender = int(ord(in_connection.recv(1)))

                            fullReceivedMessage = chr(messageLength + 1)
                            fullReceivedMessage += chr(vmSender)

                            if (vmSender == self.vmNumber):
                                print("\t\tReceived my own message")
                                dummy = in_connection.recv(messageLength)
                            else:
                                message = in_connection.recv(messageLength)
                                fullReceivedMessage += message

                                print("\t\tReceived message from " +str(hostname)+": " + message)

                                #print(message)

                                if(fullReceivedMessage not in sent_mes):
                                    mes2send.append(fullReceivedMessage)

                                else:
                                    print("\t\tAlready sent message " + str(fullReceivedMessage))


                    # NOTHING AVAILABLE ON THE SOCKET
                    except socket.error as e:
                        if(e.errno == errno.ECONNRESET):
                            pass
                            #print(e)
                        if (e.errno == errno.EAGAIN):
                            mes2send = []

                #print("\tEnd of loop mes2send " +str(mes2send))
                self.connections[address] = (hostname, in_connection, out_connection, status, mes2send[:], sent_mes[:])

            #time.sleep(2)
            count = 0

        self.shutdown()
        self.logger.info("Server: run() is done!")


#################################################

globalready = False
clientMessagesToSend = []
sentMessages = []

c = threading.Lock()

# create logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
# create console handler and set level to debug
chan = logging.StreamHandler()
chan.setLevel(logging.INFO)
# add ch to logger
logger.addHandler(chan)


run_event = threading.Event()
run_event.set()

# Start the Server thread
server = ServerSocket(num_users=USER_NUM, ip=hostName, port=PORT)
server.start()

def signal_handler(signal, frame):
    print("You pressed Control+C!")
    #client.shutdown()
    run_event.clear()
    server.join()
    exit(1)

signal.signal(signal.SIGINT, signal_handler)

### BEGINNING OF IMPORTANT STUFF
while(not globalready):
    pass

while(1):

            ## CRAFTING THE MESSAGE FROM INPUT
            # message is a string
            inputMessage = raw_input()

            # also a string
            inputMessageWithName = NAME + ": " + inputMessage
            # +1 is for the VM number added at the beginning
            #length = len(inputMessageWithName) + USER_NUM + 1
            length = len(inputMessageWithName) + 1

            # give length of full message
            inputFullMessage = chr(length)
            inputFullMessage += chr(VM_NUMBER)

            # add the message with the name
            inputFullMessage += inputMessageWithName.encode('utf-8')

            c.acquire()
            clientMessagesToSend.append(inputFullMessage)
            c.release()