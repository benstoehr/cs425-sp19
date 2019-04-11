import hashlib
import random
import copy

from block import Block


def sortFunction(x):
    return x[1]

class BlockManager(object):

    def __init__(self):

        self.blockLevel = 0
        self.bank = dict()

        self.blockchain = dict()

        self.pendingBlocks = []

        self.currentBlock = Block(level=1)
        self.currentHash = None
        self.successfulHash = None

        self.lastCommittedBlock = None

        self.currentBlockCount = 0

        self.hash = hashlib.sha256()

        self.committedTransactions = []
        self.pendingTransactions = []

        self.waitingForPuzzle = False
        self.waitingForBlockChain = False
        self.numBlocksToWaitFor = 0

        self.waitingForBlockChainFrom = None

        self.minTransactionsBeforeHash = 5
        self.maxTransactionsBeforeHash = 10
        self.numTransactionsBeforeHash = random.randint(self.minTransactionsBeforeHash, self.maxTransactionsBeforeHash)

#############
    def betterBlock(self, ip, port, message):
        block = self.singleBlockFromMessage(message)
        if(block.level > self.level):
            self.currentBlock = None
            self.incomingBlockChainIP = (ip, port)
            self.waitingForBlockChain = True
            self.numBlocksToWaitFor = block.level
            self.committedTransactions = []
            return True

        return False

    def readIncomingBlockChain(self, message):
        block = self.singleBlockFromMessage(message)

#############

    def hashCurrentBlock(self):
        h = self.hash.update(self.currentBlockAsString().encode('utf-8'))
        hh = self.hash.hexdigest()
        self.currentBlock.selfHash = hh
        return hh

#############

    def currentBlockAsString(self):
        return self.currentBlock.toMessage()

    def currentBlockAsStringWithHash(self):
        return self.currentBlock.toMessageWithHash()

    ##############

    def appendTransactionsToPending(self, transaction):
        self.pendingTransactions += [transaction]
        self.pendingTransactions.sort(key=sortFunction)

    # Adds one transaction to the current block, only happens if transaction is possible (no negatives)
    def appendTransactionToCurrentBlock(self, transaction):
        if(self.waitingForPuzzle or self.waitingForBlockChain):
            if (transaction not in self.pendingTransactions):
                print("\t\tP" + str(transaction))
                self.appendTransactionsToPending(transaction)
            return

        print("\t" + str(transaction))
        self.currentBlock.addTransactionToBlock(transaction)
        if(transaction in self.pendingTransactions):
            self.pendingTransactions.remove(transaction)
            
        self.currentBlockCount += 1
        if(self.currentBlock.transactionCount == self.numTransactionsBeforeHash):
            blockHash = self.hashCurrentBlock()
            self.currentHash = blockHash
            self.currentBlock.selfHash = blockHash
            self.currentBlockCount = 0
            self.numTransactionsBeforeHash = random.randint(self.minTransactionsBeforeHash, self.maxTransactionsBeforeHash)
            self.waitingForPuzzle = True

    def appendPendingTransactionsToNewBlock(self):
        print("appendPendingTransactionsToNewBlock()")
        for pt in self.pendingTransactions:
            self.appendTransactionToCurrentBlock(pt)

##############

    def successfulBlock(self, message):
        [wordBLOCK, hashOfBlock, puzzleAnswer] = message
        #print("BLOCK MANAGER currentHash: " + str(self.currentHash))
        #print("BLOCK MANAGER currentBlock.selfHash: " + str(self.currentBlock.selfHash))
        #print("BLOCK MANAGER hashOfBlock: " + str(hashOfBlock))
        if(self.currentBlock.selfHash == hashOfBlock):
            print("BLOCK SUCCESS")
            self.currentBlock.puzzleAnswer = puzzleAnswer
            self.blockchain[self.currentBlock.level] = self.currentBlock
            self.waitingForPuzzle = False
            return True
        return False

    def newBlock(self):
        print("newBlock()")
        previousLevel = self.currentBlock.level
        previousHash = self.currentBlock.selfHash
        self.lastCommittedBlock = copy.deepcopy(self.currentBlock)
        self.currentBlock = Block(level=(previousLevel + 1), previousHash=previousHash)
        self.currentHash = None

    def fillNewBlock(self):
        print("fillNewBlock()")
        self.appendPendingTransactionsToNewBlock()



###### Messages to Blocks #####

    def singleBlockFromMessage(self, byteString):
        block = Block()
        hash, level, content = byteString.split("$")
        block.previousBlock = hash

        for transaction in content.split(":"):
            splitTransaction = transaction.split("_")
            block.txIDs.append(splitTransaction[2])
            block.transactions.append(transaction.replace("_"," "))
        return block


    def multipleBlocksFromMessage(self, longByteString):
        blocks = []
        # block will be a string
        for block in longByteString.split("^"):
            blocks.append(self.singleBlockFromMessage(block))
        return blocks

################# Console Logging #################

    def printCurrentBlock(self):
        if(self.currentBlock is not None):
            self.currentBlock.printSelf()

