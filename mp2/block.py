import hashlib


def sortFunction(x):
    return x[1]

class Block(object):

    def returnTransactions(self):
        return self.transactions;

    def returnTxIDs(self):
        return self.txIDs

    def __init__(self):

        self.level = None
        # String Hash
        self.previousBlock = None

        # Floats with 6 decimals
        self.firstTransactionTime = None
        self.lastTransactionTime = None

        # 128 bit Hash
        self.txIDs = []

        # Array of arrays [[TRANSACTION, 1554767825.606276, 6d46d036a7276ae3753da0adca3120cc, 708914, 967451, 15]]
        self.transactions = []


    #TODO:
    #transaction will be an array
    def addTransactionToBlock(self, transaction):
        self.transactions.append(transaction)
        self.transactions.sort(key=sortFunction)

    #TODO:
    def toMessage(self):
        string = ""
        if(self.previousBlock is not None):
            string += self.previousBlock + "$"
        else:
            string += "0$"
        for transaction in self.transactions:
            string += "_".join(transaction)
            string += ":"
        string += "^"
        return string






