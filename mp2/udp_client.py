import socket

UDP_IP_ADDRESS = "127.0.0.1"
UDP_PORT_NO = 6789

n = 0

clientSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

while True:

    message = "This is message {}".format(n).encode("utf-8")
    clientSock.sendto(message, (UDP_IP_ADDRESS, UDP_PORT_NO))
    n += 1

    if n >= 10:
        break
