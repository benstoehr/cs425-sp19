import time

class Logger():

    def __init__(self, logger, myIP, myPort, vmNumber, name, serviceIP, servicePort):
        self.masterLogging = logger
        self.ip = myIP
        self.port = myPort
        self.vmNumber = vmNumber
        self.name = name
        self.serviceIP = serviceIP
        self.servicePort = servicePort

    ## ONLY FOR MESSAGES FROM OTHER NODES
    def getIPandPort(self, message):

        bytes = len(message)
        message = message.split()
        ip, port = message[0].split(":")

        ip = str(ip)
        port = int(port)

        return ip, port, message[1:], bytes

    def pullIPoffOutgoing(self, message):
        bytes = len(message)
        message = message.split()
        return message[1:], bytes


    def plainLog(self, message):
        self.masterLogging.debug(message)

    ## SERVICE MESSAGES
    def logServiceTransaction(self, ip, port, message):

        timestamp_a = time.time()
        ttype = "TRANSACTION"
        tID = message[2]
        mess = str("_".join(message))
        bytes = len(mess)
        fromNode = str(ip) + "," + str(port)
        toNode = str(self.ip) + "," + str(self.port)
        sentTime = message[1]
        status = "ServiceTransaction"
        nodeNum = self.vmNumber
        bytes = len(mess)

        fileString = '{0:.6f}'.format(timestamp_a) + " " + str(self.name) + " " + str(status) + " " + str(bytes) + " " + str(ttype) + " " + str(tID) + " " + str(
            fromNode) + " " + str(toNode) + " " + str(sentTime)  + "\n"
        self.masterLogging.debug(fileString)

    def logServiceIntroduction(self, ip, port, message):

        timestamp_a = time.time()
        ttype = "INTRODUCE"
        tID = None
        mess = str("_".join(message))
        fromNode = str(ip) + "," + str(port)
        toNode = str(self.ip) + "," + str(self.port)
        sentTime = None
        status = "ServiceIntroduction"
        nodeNum = self.vmNumber
        bytes = len(mess)

        fileString = '{0:.6f}'.format(timestamp_a) + " " + str(self.name) + " " + str(status) + " " + str(bytes) + " " + str(
            ttype) + " " + str(tID) + " " + str(fromNode) + " " + str(toNode) + " " + str(sentTime) + "\n"
        self.masterLogging.debug(fileString)

    def logServiceVerify(self):
        pass


## NODE MESSAGES

    ## CP1
    def logReceivedTransaction(self, message):

        ip, port, message, bytes = self.getIPandPort(message)

        timestamp_a = time.time()
        ttype = "TRANSACTION"
        tID = message[2]
        mess = str("_".join(message))
        fromNode = str(ip) + "," + str(port)
        toNode = str(self.ip) + "," + str(self.port)
        sentTime = message[1]
        status = "IncomingNodeTransaction"
        nodeNum = self.vmNumber

        fileString = '{0:.6f}'.format(timestamp_a) + " " + str(self.name) + " " + str(status) + " " + str(bytes) + " " + str(
            ttype) + " " + str(tID) + " " + str(fromNode) + " " + str(toNode) + " " + str(sentTime) + "\n"
        self.masterLogging.debug(fileString)

    def logSentTransaction(self, ip, port, message):

        pureMessage, bytes = self.pullIPoffOutgoing(message)

        timestamp_a = time.time()
        ttype = "TRANSACTION"
        tID = pureMessage[2]
        mess = str("_".join(pureMessage))
        fromNode = str(self.ip) + "," + str(self.port)
        toNode = str(ip) + "," + str(port)
        sentTime = pureMessage[1]
        status = "OutgoingNodeTransaction"
        nodeNum = self.vmNumber

        fileString = '{0:.6f}'.format(timestamp_a) + " " + str(self.name) + " " + str(status) + " " + str(bytes) + " " + str(
            ttype) + " " + str(tID) + " " + str(fromNode) + " " + str(toNode) + " " + str(sentTime) + "\n"
        self.masterLogging.debug(fileString)

    def logReceivedIntroduction(self, message):

        ip, port, message, bytes = self.getIPandPort(message)

        timestamp_a = time.time()
        ttype = "INTRODUCE"
        tID = None
        mess = str("_".join(message))
        fromNode = str(ip) + "," + str(port)
        toNode = str(self.ip) + "," + str(self.port)
        sentTime = None
        status = "IncomingNodeIntroduction"
        nodeNum = self.vmNumber

        fileString = '{0:.6f}'.format(timestamp_a) + " " + str(self.name) + " " + str(status) + " " + str(bytes) + " " + str(
            ttype) + " " + str(tID) + " " + str(fromNode) + " " + str(toNode) + " " + str(sentTime) + "\n"
        self.masterLogging.debug(fileString)

    def logSentIntroduction(self, ip, port, message):

        pureMessage, bytes = self.pullIPoffOutgoing(message)

        timestamp_a = time.time()
        ttype = "INTRODUCE"
        tID = None
        mess = str("_".join(pureMessage))
        fromNode = str(self.ip) + "," + str(self.port)
        toNode = str(ip) + "," + str(port)
        sentTime = None
        status = "OutgoingNodeIntroduction"
        nodeNum = self.vmNumber

        fileString = '{0:.6f}'.format(timestamp_a) + " " + str(self.name) + " " + str(status) + " " + str(bytes) + " " + str(
            ttype) + " " + str(tID) + " " + str(fromNode) + " " + str(toNode) + " " + str(sentTime) + "\n"
        self.masterLogging.debug(fileString)


    ## CP2
    # Passed in as string
    def logReceivedBlock(self, selfHash, fullMessage):
        
        ip, port, message, bytes = self.getIPandPort(fullMessage)

        timestamp_a = time.time()
        status = "IncomingBlock"
        ttype = "BLOCK"
        tID = selfHash
        mess = message
        fromNode = str(ip) + "," + str(port)
        toNode = str(self.ip) + "," + str(self.port)
        sentTime = None

        nodeNum = self.vmNumber

        fileString = '{0:.6f}'.format(timestamp_a) + " " + str(self.name) + " " + str(status) + " " + str(bytes) + " " + str(
            ttype) + " " + str(tID) + " " + str(fromNode) + " " + str(toNode) + " " + str(sentTime) + "\n"
        self.masterLogging.debug(fileString)

    def logSentBlock(self, selfHash, message, ip, port):
        #print("logSentBlock()")
        pureMessage, bytes = self.pullIPoffOutgoing(message)

        timestamp_a = time.time()
        status = "OutgoingBlock"
        ttype = "BLOCK"
        tID = selfHash
        mess = pureMessage
        fromNode = str(self.ip) + "," + str(self.port)
        toNode = str(ip) + "," + str(port)
        sentTime = None

        nodeNum = self.vmNumber

        fileString = '{0:.6f}'.format(timestamp_a) + " " + str(self.name) + " " + str(status) + " " + str(bytes) + " " + str(
            ttype) + " " + str(tID) + " " + str(fromNode) + " " + str(toNode) + " " + str(sentTime) + "\n"
        self.masterLogging.debug(fileString)

    # Node to Service about personal block

    def logReceivedPuzzle(self, message):

        print("logReceivedPuzzle()")
        timestamp_a = time.time()
        ttype = "SOLVED"
        tID = message[1]
        mess = str("_".join(message))
        fromNode = str(self.serviceIP) + "," + str(self.servicePort)
        toNode = str(self.ip) + "," + str(self.port)
        sentTime = None
        status = "IncomingSolvedPuzzle"
        nodeNum = self.vmNumber

        fileString = '{0:.6f}'.format(timestamp_a) + " " + str(self.name) + " " + str(status) + " " + str(bytes) + " " + str(
            ttype) + " " + str(tID) + " " + str(fromNode) + " " + str(toNode) + " " + str(sentTime) + "\n"
        self.masterLogging.debug(fileString)

    def logSentPuzzle(self, message):

        solveWord, hash = message.split(" ")

        timestamp_a = time.time()
        status = None
        bytes = len(message)
        ttype = "SOLVE"
        tID = hash
        mess = message
        fromNode = str(self.ip) + "," + str(self.port)
        toNode = str(self.serviceIP) + "," + str(self.servicePort)
        sentTime = None
        status = "OutgoingPuzzle"
        nodeNum = self.vmNumber

        fileString = '{0:.6f}'.format(timestamp_a) + " " + str(self.name) + " " + str(status) + " " + str(bytes) + " " + str(
            ttype) + " " + str(tID) + " " + str(fromNode) + " " + str(toNode) + " " + str(sentTime) + "\n"
        self.masterLogging.debug(fileString)

    # Node to Service about incoming block
    # OOPSEY

    def logReceivedVerify(self):

        ip, port, message, bytes = self.getIPandPort(message)

        timestamp_a = time.time()
        ttype = "VERIFY" + "-" + message[1] # OK or FAIL
        tID = pureMessage[1] + "_" + pureMessage[2]
        mess = str("_".join(message))
        fromNode = str(ip) + "," + str(port)
        toNode = str(self.ip) + "," + str(self.port)
        sentTime = None
        status = "IncomingVerify"
        nodeNum = self.vmNumber

        fileString = '{0:.6f}'.format(timestamp_a) + " " + str(self.name) + " " + str(status) + " " + str(bytes) + " " + str(
            ttype) + " " + str(tID) + " " + str(fromNode) + " " + str(toNode) + " " + str(sentTime) + "\n"
        self.masterLogging.debug(fileString)

    def logSentVerify(self):
        
        pureMessage, bytes = self.pullIPoffOutgoing(message)

        timestamp_a = time.time()
        ttype = "VERIFY"
        tID = pureMessage[1] + "_" + pureMessage[2]
        mess = str("_".join(pureMessage))
        fromNode = str(self.ip) + "," + str(self.port)
        toNode = str(ip) + "," + str(port)
        sentTime = None
        status = "OutgoingVerify"
        nodeNum = self.vmNumber

        fileString = '{0:.6f}'.format(timestamp_a) + " " + str(self.name) + " " + str(status) + " " + str(bytes) + " " + str(
            ttype) + " " + str(tID) + " " + str(fromNode) + " " + str(toNode) + " " + str(sentTime) + "\n"
        self.masterLogging.debug(fileString)


