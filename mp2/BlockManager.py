import hashlib
import random

from block import Block

class BlockManager(object):

    def __init__(self):

        self.blockLevel = 0
        self.bank = dict()

        self.blockchain = dict()

        self.pendingBlocks = []

        self.currentBlock = None
        self.currentHash = None
        self.successfulHash = None

        self.currentBlockCount = 0

        self.hash = hashlib.sha256()

        self.pendingTransactions = []

        self.waitingForPuzzle = False
        self.waitingForBlockChain = False
        self.numBlocksToWaitFor = 0

        self.waitingForBlockChainFrom = None

        self.numTransactionsBeforeHash = int(random.random() * 20)

#############
    def betterBlock(self, ip, port, message):
        block = self.singleBlockFromMessage(message)
        if(block.level > self.level):
            self.currentBlock = None
            self.incomingBlockChainIP = (ip, port)
            self.waitingForBlockChain = True
            self.numBlocksToWaitFor = block.level
            return True

        return False

    def readIncomingBlockChain(self, message):
        block = self.singleBlockFromMessage(message)

#############
    def hashCurrentBlock(self):
        h = self.hash.update(self.currentBlockAsString().encode('utf-8'))
        self.currentBlock.selfHash = h
        return self.hash.hexdigest()

#############

    def currentBlockAsString(self):
        return self.currentBlock.toMessage()

    def currentBlockAsStringWithHash(self):
        return self.currentBlock.toMessageWithHash()

##############

    def appendTransactionsToPending(self, transaction):
        self.pendingTransactions += [transaction
                                     ]
    # Adds one transaction to the current block, only happens if transaction is possible (no negatives)
    def appendTransactionToCurrentBlock(self, transaction):
        if(self.waitingForPuzzle or self.waitingForBlockChain):
            self.appendTransactionsToPending(transaction)
            return

        self.currentBlock.addTransactionToBlock(transaction)
        self.currentBlockCount += 1
        if(self.currentBlock.transactionCount == self.numTransactionsBeforeHash):
            self.currentHash = self.hashCurrentBlock()
            self.currentBlockCount = 0
            self.numTransactionsBeforeHash = int(random.random() * 20)
            self.waitingForPuzzle = True


###### Sending STUFF #####

    def successfulBlock(self, message):
        wordBLOCK, hashOfBlock, puzzleAnswer = message.split(' ')
        if(self.currentBlock.selfHash == hashOfBlock):
            self.currentBlock.puzzleAnswer = puzzleAnswer
            return True
        return False


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

