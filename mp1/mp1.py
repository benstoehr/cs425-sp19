# This is our mp1 code.
# To run our chat client enter "python3 mp1.py <port> <number of participants>
#
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



#server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

IP_ADDR = ''

# Addresses of other VMs for mp1
# VM0 = 'sp19-cs425-g32-01.cs.illinois.edu'
# VM1 = 'sp19-cs425-g32-02.cs.illinois.edu'
# VM2 = 'sp19-cs425-g32-03.cs.illinois.edu'
# VM3 = 'sp19-cs425-g32-04.cs.illinois.edu'
# VM4 = 'sp19-cs425-g32-05.cs.illinois.edu'
# VM5 = 'sp19-cs425-g32-06.cs.illinois.edu'
# VM6 = 'sp19-cs425-g32-07.cs.illinois.edu'
# VM7 = 'sp19-cs425-g32-08.cs.illinois.edu'
# VM_LIST = [VM0, VM1, VM2, VM3, VM4, VM5, VM6, VM7]

# Addresses of other VMs for mp1
VM0 = 'sp19-cs425-g58-01.cs.illinois.edu'
VM1 = 'sp19-cs425-g58-02.cs.illinois.edu'
VM2 = 'sp19-cs425-g58-03.cs.illinois.edu'
VM3 = 'sp19-cs425-g58-04.cs.illinois.edu'
VM4 = 'sp19-cs425-g58-05.cs.illinois.edu'
VM5 = 'sp19-cs425-g58-06.cs.illinois.edu'
VM6 = 'sp19-cs425-g58-07.cs.illinois.edu'
VM7 = 'sp19-cs425-g58-08.cs.illinois.edu'
VM_LIST = [VM0, VM1, VM2, VM3, VM4, VM5, VM6, VM7]

#CUR_VM = 0
#del VM_LIST[CUR_VM]


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

            #self.sock.setblocking(False)

        else:
            self.sock = sock

        self.ip = ip
        self.port = port

        self.numberOfUsers = num_users - 1

        self.connections = dict()
        self.messageQueue = []
        self.ready = False
        self.activeConnections = 0

        # create logger
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        # create console handler and set level to debug
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        # add ch to logger
        self.logger.addHandler(ch)


    def bind(self, ip_addr, port):
        # binds the server to IP and at the specified port number

        #self.logger.info("ip_addr: " + str(ip_addr))
        #self.logger.info("port: " + str(port))

        bindCheck = self.sock.bind((ip_addr, port))
        #self.logger.info("bindCheck: " + str(bindCheck))
        # if (bindCheck != 0):
        #     print("Error occured at self.sock.bind()")
        # listens for 8 active connections.
        #self.sock.listen(8)
        # listens for N active connections
        listenCheck = self.sock.listen(self.numberOfUsers)
        #self.logger.info("listenCheck: " + str(listenCheck))
        # if(listenCheck != 0):
        #     print("Error occured at self.sock.listen()")

    def acceptConnections(self):

        self.bind(self.ip, self.port)

        #sys.stdout.write("Server: START ACCEPTING CONNECTIONS!\n")
        #sys.stdout.flush()

        acceptConnectionsStart = time.time()

        while(not self.ready):
            print("serverWhile")

            currentTime = time.time()
            if(currentTime - acceptConnectionsStart > 20000):
                self.logger.info("Server: 20 second timeout exceeding when waiting for connections")

            # Accept a single connection
            if(self.sock is not None):
                #self.logger.info("Server: CALLING ACCEPT()")
                try:
                    connection, address = self.sock.accept()
                    connection.setblocking(0)

                    # Add connection to connection list
                    self.connections[address] = (connection, 'active')
                    self.logger.info('Server: Connection established by: '+ str(address))
                    self.activeConnections += 1

                except socket.error as error:
                    #self.logger.info("Server: CAUGHT SOCKET ERROR WTF")
                    pass

            else:
                self.logger.info("Server: self.sock is None in acceptConnections")


            # Once the proper number of connections is made, exit the while loop
            if(self.activeConnections == (USER_NUM - 1)):
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

        #print("Server: INSIDE THE RUN FUNCTION")
        self.acceptConnections()

        while(not self.ready):
            #self.logger.info("Server: NOT READY YET!")
            time.sleep(1)

        count = 0

        while(run_event.is_set()):
            # TODO: Main server logic
            # iterate over each connection and read 8 bytes for message length
            #
            #self.logger.info("Server: In the main loops")


            for address, (connection, status) in self.connections.items():
                if(status == 'active'):
                    try:
                        #print("Server: recv(1) " + str(address))

                        receiveCheck = connection.recv(1)
                        if(receiveCheck == -1):
                            print("Server: receiveCheck == -1")

                        # THIS MEANS THE CONNECTION CLOSED
                        elif(len(receiveCheck) == 0):
                            print("Server: receiveCheck: nothing to read")
                            print(str(address) + " disconnected!")
                            self.connections[address] = (connection, 'inactive')

                        elif(len(receiveCheck) > 0):
                            #print("Server: receiveCheck > 0: " + str(ord(receiveCheck)))
                            #if(receiveCheck == "0"):
                            #    print("HB")
                            #else:
                            message = connection.recv(ord(receiveCheck))
                            print("Server: Received message: " + str(message))

                    except socket.error as e:
                        if(e.errno == errno.ECONNRESET):
                            pass
                        if (e.errno == errno.EAGAIN):
                            pass
                        else:
                            #print("Server: Other error calling connection.recv()!")
                            print("Error: " + str(errno.errorcode[e.errno]))


            time.sleep(1)
            count += 1
            if(count == 100):
                break
            continue

        self.logger.info("Server: run() is done!")


class ClientSocket():

    def __init__(self, sock=None, num_users=USER_NUM, username=NAME):
        if sock is None:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        else:
            self.sock = sock

        self.connections = dict()
        self.num_users = num_users - 1
        self.activeConnections = 0
        self.name = socket.gethostname()
        self.username = username

        self.vector = []
        for i in range(num_users):
            self.vector.append(0)

    def connectToServers(self):

        connectionStartTime = time.time()

        servers = VM_LIST[:(self.num_users + 1)]
        #print("Client: Servers: " +str(servers))

        #print("Client: NAME: " + str(self.name))
        servers.remove(self.name)

        attemptCount = 0
        while(self.activeConnections != self.num_users):

            print("clientWhile")
            curr_time = time.time()
            if(curr_time - connectionStartTime > 30000):
                print("Client: 30 second timeout for connecting to servers")
                break

            connectionIndex = attemptCount % self.num_users
            server = servers[connectionIndex]

            if(server in self.connections.keys()):
                attemptCount += 1
                continue

            # Try connecting to servers
            try:
                new_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                new_connection.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                connectCheck = new_connection.connect((server, PORT))

            except socket.error as e:
                print(errno.errorcode[e.errno])
                #self.connections[server] = (None, 'inactive')
                new_connection.close()
                attemptCount += 1
                time.sleep(1)
                continue


            print("Client: Connected to server " + str(server))
            self.activeConnections += 1
            self.connections[server] = (new_connection, 'active')
            attemptCount += 1
            continue


            time.sleep(1)

        # Check to ensure all the connections are made
        if(self.activeConnections == self.num_users):
            #print("Client: Connected to " + str(self.num_users) + " servers!")
            print("Client: I'M READY!")
        else:
            print("Client: Error connecting to servers! SORRY")


    def heartbeat(self):
        for serverName, connection in self.connections.items():
            connection.send("\x00")

    def mainLoop(self):
        while(1):
            # message is a string
            message = raw_input()
            # also a string
            messageWithName = self.username + ": " + message

            length = len(messageWithName) + USER_NUM + 1

            # give length of full message
            fullMessage = chr(length)

            # include the vector timestamp
            for i in range(self.num_users + 1):
                if(i+1 == int(VM_NUMBER)):
                    fullMessage += chr(self.vector[i] + 1)
                else:
                    fullMessage += chr(self.vector[i])

            # add the message with the name
            fullMessage += messageWithName.encode('utf-8')

            print("Client: " + str(fullMessage))


            for serverName, (connection, status) in self.connections.items():
                if(status == 'active' and connection is not None):
                    try:
                        connection.send(fullMessage)
                    except socket.error as e:
                        if(e == 'Broken pipe'):
                            print("Broken pipe to connection " + str(serverName) + " changing status")
                            self.connections[serverName] = (connection, 'inactive')

    def shutdown(self):
        for serverName, (connection, status) in self.connections.items():
            if(status == 'active' and connection is not None):
                connection.close()

        self.sock.close()


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

#time.sleep(5)
# # Start the client
client = ClientSocket(num_users=USER_NUM)
client.connectToServers()
client.mainLoop()


#print("READY FOR ACTION!!!!")

# TODO: Change to a looping while to accept all connections
# include timeout from start of program

# TODO: Main logic loop
# Every second look for message from all nodes, if missing, mark node as a failure

# TODO:
