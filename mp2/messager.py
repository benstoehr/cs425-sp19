class Messager(object):

    numMessages = None

    def __init__(self):
        self.numMessages = 0

    def isTransaction(self, message):
        if("TRANSACTION" in message):
            return True

    def getMessageType(self, message):

        if(message is None):
            return None
        elif("TRANSACTION" in message):
            return "TRANSACTION"
        elif("INTRODUCE" in message):
            return "INTRODUCE"
        elif ("QUIT" in message):
            return "QUIT"
        elif ("DIE" in message):
            return "DIE"
        elif ("REPLY" in message):
            return "REPLY"
        else:
            return "WOOP"



