import hashlib


def sortFunction(x):
    return x[1]

class Block(object):

    def returnTransactions(self):
        return self.transactions;

    def returnTxIDs(self):
        return self.txIDs

    def __init__(self, level=None, previousHash=None):

        self.level = level

        # String Hash
        self.previousBlockHash = None
        self.selfHash = None
        self.puzzleAnswer = None

        # Floats with 6 decimals
        self.firstTransactionTime = None
        self.lastTransactionTime = None

        # 128 bit Hash
        self.txIDs = []

        # Array of arrays [[TRANSACTION, 1554767825.606276, 6d46d036a7276ae3753da0adca3120cc, 708914, 967451, 15]]
        self.transactions = []
        self.transactionCount = 0

    #TODO:
    #transaction will be an array
    def addTransactionToBlock(self, transaction):
        self.transactionCount += 1
        self.transactions.append(transaction)
        self.transactions.sort(key=sortFunction)


    #TODO:
    #BLOCK MESSAGE = [ <previous hash> $ <level> $ <transactions> ^ ]
    def toMessage(self):
        string = ""
        if(self.previousBlockHash is not None):
            string += self.previousBlockHash + "$"
        else:
            string += "0$"
        string += str(self.level)
        for transaction in self.transactions:
            string += "_".join(transaction)
            string += ":"
        string += "^"
        return string

    def toMessageWithHash(self):
        string = ""
        if(self.previousBlockHash is not None):
            string += self.previousBlockHash + "$"
        else:
            string += "0$"
        string += str(self.level)
        for transaction in self.transactions:
            string += "_".join(transaction)
            string += ":"
        string += self.selfHash
        string += "^"
        return string


    def printSelf(self):
        for t in self.transactions:
            print("\t" + str(t))







