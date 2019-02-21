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
print("hostName: " + str(hostName))

splitHostName = hostName.split("-")
VM_NUMBER = splitHostName[3].split(".")[0]
print("Running on VM: " +  str(VM_NUMBER))

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

        self.activeConnections = 0
        self.connections = dict()

        self.sentMessages = []
        self.messageQueue = []

        self.ready = False

        # create logger
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        # create console handler and set level to debug
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        # add ch to logger
        self.logger.addHandler(ch)

    def bind(self, ip_addr, port):
        bindCheck = self.sock.bind((ip_addr, port))
        listenCheck = self.sock.listen(self.numberOfClients)

    def initializeConnections(self):

        self.bind(self.ip, self.port)

        initializeConnectionsStart = time.time()

        while(not self.ready):
            print("serverWhile")

            currentTime = time.time()
            if(currentTime - initializeConnectionsStart > 20000):
                self.logger.info("Server: 20 second timeout exceeding when waiting for connections")

            if(self.sock is not None):
                #self.logger.info("Server: CALLING ACCEPT()")
                try:

                    connection, address = self.sock.accept()
                    connection.setblocking(0)

                    # if the address has been seen, it was seen when trying to connect to other clients
                    if(address in self.connections.keys()):
                        connection.close()
                    # Otherwise add connection to connection list
                    else:
                        self.connections[address] = (None , connection, 'active')

                    self.logger.info('Server: Connection established by: '+ str(address))
                    self.activeConnections += 1

                except socket.error as error:
                    print("no connections yet")
                    print(error)

            else:
                self.logger.info("Server: self.sock is None in acceptConnections")

            for vm in VM_LIST:

                if(vm == self.hostname):
                    continue
                    
                new_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                new_connection.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

                try:
                    connectCheck = new_connection.connect((vm, self.port))
                    new_connection.setblocking(0)

                    ip = new_connection.getpeername()
                    # already connected to this ip, update the vm hostname
                    if(ip in self.connections.keys()):
                        (tempserver, connection, status) = self.connections[ip]
                        if(tempserver is None):
                            self.connections[ip] = (server, connection, 'active')

                    else:
                        self.connections[ip] = (server, new_connection, 'active')
                        self.activeConnections += 1

                except socket.error as e:
                    #print(errno.errorcode[e.errno])
                    #self.connections[server] = (None, 'inactive')
                    new_connection.close()
                    continue

            # Once the proper number of connections is made, exit the while loop
            if(self.activeConnections == self.numberOfClients):
                self.ready = True
                self.logger.info("Server: CONNECTED TO ALL THE CLIENTS!")

            time.sleep(1)

    def shutdown(self):
        for address, (connection, status) in self.connections.items():
            if(status == 'active' and connection is not None):
                connection.close()

        self.sock.close()
        exit(1)

    def run(self):

        # make vector global
        global vector
        global sentMessages
        global messagesToSend

        #print("Server: INSIDE THE RUN FUNCTION")
        self.initializeConnections()

        while(not self.ready):
            #self.logger.info("Server: NOT READY YET!")
            time.sleep(1)

        count = 0

        while(run_event.is_set()):
            # TODO: Main server logic
            # iterate over each connection and read 8 bytes for message length

            count = 0


        self.shutdown()
        self.logger.info("Server: run() is done!")


#################################################

# Start the Server thread
server = ServerSocket(num_users=USER_NUM, ip=hostName, port=PORT)
server.start()

def signal_handler(signal, frame):
    print("You pressed Control+C!")
    client.shutdown()
    run_event.clear()
    server.join()
    exit(1)

signal.signal(signal.SIGINT, signal_handler)

### BEGINNING OF IMPORTANT STUFF

run_event = threading.Event()
run_event.set()