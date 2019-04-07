import time

class Logger():

    def __init__(self, logger, myIP, myPort, vmNumber):
        self.masterLogging = logger
        self.ip = myIP
        self.port = myPort
        self.vmNumber = vmNumber


    def getIPandPort(self, message):
        bytes = len(message)
        message = message.split()
        ip, port = message[0].split(":")

        ip = str(ip)
        port = int(port)

        return ip, port, message, bytes

    def logReceivedTransaction(self, message):

        ip, port, message, bytes = self.getIPandPort(message)
        timestamp_a = message[1]
        ttype = "TRANSACTION"
        txID = message[2]
        mess = str("_".join(message))
        fromNode = str(ip) + "," + str(port)
        toNode = str(self.ip) + "," + str(self.port)
        sentTime = time.time()
        status = "alive"
        nodeNum = self.vmNumber


        fileString = " " + str(timestamp_a) + " " + str(ttype) + " " + str(txID) + " " + str(mess) + " " + str(
            fromNode) + " " + str(toNode) + " " + str(sentTime) + " " + str(status) + " " + str(
            nodeNum) + " " + str(bytes) + "\n"

        self.masterLogging.debug(fileString)




    def logSentTransaction(self):
        pass

    def logReceivedIntroduction(self):
        pass

    def logSentIntroduction(self):
        pass

    def logReceivedBlock(self):
        pass

    def logSentBlock(self):
        pass

    def logReceivedPuzzle(self):
        pass

    def logSentPuzzle(self):
        pass

    def logReceivedVerify(self):
        pass

    def logSentVerify(self):
        pass


