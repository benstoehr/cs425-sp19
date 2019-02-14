import socket
import sys

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
              
IP_ADDR = '' 
VM0 = 'sp19-cs425-g32-01.cs.illinois.edu'
VM1 = 'sp19-cs425-g32-02.cs.illinois.edu'
VM2 = 'sp19-cs425-g32-03.cs.illinois.edu'
VM3 = 'sp19-cs425-g32-04.cs.illinois.edu'
VM4 = 'sp19-cs425-g32-05.cs.illinois.edu'
VM5 = 'sp19-cs425-g32-06.cs.illinois.edu'
VM6 = 'sp19-cs425-g32-07.cs.illinois.edu'
VM7 = 'sp19-cs425-g32-08.cs.illinois.edu'
VM_LIST = [VM0, VM1, VM2, VM3, VM4, VM5, VM6, VM7]
CUR_VM = 0
del VM_LIST[CUR_VM]
        
# takes the first argument from command prompt as user name
NAME = str(sys.argv[1])

# takes the second argument from command prompt as port number 
PORT = int(sys.argv[2])

# takes the third argument from command prompt as user number 
USER_NUM = int(sys.argv[3])

class ServerSocket:
    conn_list = []
    msg_queue = {}
    def __init__(self, sock=None):
        if sock is None:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        else:
            self.sock = sock

    def bind(self, ip_addr, port):
        # binds the server to IP and at the specified port number
        self.sock.bind((ip_addr, port))
        # listens for 8 active connections.
        self.sock.listen(8)

    def accept(self):
        conn, addr = self.sock.accept()
        conn_list.append(conn)
        print('# Connected by', addr)
        self.client_conn(conn, addr)
        """
        while True:
            data = conn.recv(1024)
            print('# Received', repr(data))
            conn.sendall(data)
            if not data:
                print('# Connection ', addr, ' is closed')
                conn.close()
                break
        """

    def client_conn(self, conn, addr): 
  
        # sends a message to the client whose user object is conn 
        conn.send(b'Welcome to this chatroom!')
        user_name = ''
        n = 0
        while True: 
            #try:
            msg = conn.recv(1024)
            if not msg:
                """message may have no content if the connection 
                is broken, in this case we remove the connection"""
                print('# Connection ', addr, ' is closed')
                conn.close()
                break

            else: 
                if n == 0:
                    # record the user name
                    user_name = msg.decode('utf-8')
                    print('# {} joins the chat.'.format(user_name))
                    conn.sendall(msg)
                    n += 1
                else:
                    """prints the message and address of the 
                    user who just sent the message on the server 
                    terminal"""
                    named_msg = user_name + ': ' + msg.decode('utf-8')
                    print(named_msg)
                    conn.sendall(msg)
                    n += 1
                    # Calls broadcast function to send message to all 
                    #message_to_send = "<" + addr[0] + "> " + message 
                    #broadcast(message_to_send, conn) 
  
            #except: 
            #    continue

class ClientSocket:
    def __init__(self, sock=None):
        if sock is None:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        else:
            self.sock = sock

    def connect(self, host):
        self.sock.connect((host, PORT))
        self.sock.send(NAME)
        self.sock.recv(1024)

    def send(self, msg):
        ts = [1,0,0,0]
        ts_byte = ','.join(ts).encode('utf-8')
        self.sock.send(ts_byte)
        self.sock.recv(1024)
        self.sock.send(msg.encode('utf-8'))
        self.sock.recv(1024)

def send_input(client_list):
    msg = input()
    for client in client_list:
        client.send(msg.encode('utf-8'))
    print(msg)

def client_conn(user_num):
    client_socks = []
    for i in range(user_num-1):
        s = ClientSocket()
        s.connect(VM_LIST[i])
        client_socks.append(s)

    while True:
        send_input(client_socks)

server = ServerSocket()
server.bind(IP_ADDR, PORT)
server.accept()

client_conn(USER_NUM)


