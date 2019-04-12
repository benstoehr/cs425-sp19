import hashlib


def sortFunction(x):
    return x[1]

class Block(object):

    def returnTransactions(self):
        return self.transactions;

    def returnTxIDs(self):
        return self.txIDs

    def __init__(self, level=None, previousHash=None, puzzle=None):

        self.level = level

        # String Hash
        self.previousBlockHash = previousHash
        self.selfHash = None
        self.puzzleAnswer = puzzle

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
    #BLOCK MESSAGE = [ BLOCK <previous hash>$<level>$<transactions>^]
    def toMessage(self):
        string = "BLOCK "
        if(self.previousBlockHash is not None):
            string += self.previousBlockHash + "$"
        else:
            string += "0$"
        string += str(self.level)
        string += "$"
        for transaction in self.transactions[:-1]:
            string += "_".join(transaction)
            string += "*"
        string += "_".join(self.transactions[-1])
        string += "^"
        return string 

    def toMessageWithHash(self):
        string = "BLOCK "
        if(self.previousBlockHash is not None):
            string += self.previousBlockHash + "$"
        else:
            string += "0$"
        string += str(self.level)
        string += "$"
        for transaction in self.transactions[:-1]:
            string += "_".join(transaction)
            string += "*"
        string += "_".join(self.transactions[-1])
        string += "$"
        string += str(self.puzzleAnswer)
        string += "^"
        return string

    def toChainMessage(self):
        string = "BLOCKCHAIN "
        if(self.previousBlockHash is not None):
            string += self.previousBlockHash + "$"
        else:
            string += "0$"
        string += str(self.level)
        string += "$"
        for transaction in self.transactions[:-1]:
            string += "_".join(transaction)
            string += "*"
        string += "_".join(self.transactions[-1])
        string += "$"
        string += str(self.puzzleAnswer)
        string += "^"
        return string

    def getTransactions(self):
        return self.transactions

    def gettxIDs(self):
        txIDs = []
        for t in self.transactions:
            txIDs += [str(t[2])]

    def printSelf(self):
        print("[BLOCK " + str(self.level) + "]")
        print("[PREVIOUS:" + str(self.previousBlockHash) + "]")
        print("[HASH:" + str(self.selfHash) + "]")
        print("[PUZZLE: " + str(self.puzzleAnswer) + "]")
        for t in self.transactions:
            print(str(t))
        print("")