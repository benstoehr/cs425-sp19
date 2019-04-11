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

        self.obsoleteHashes = []

        self.currentBlock = Block(level=1)

        self.lastSuccessfulHash = None
        self.lastSuccessfulBlock = None

        self.currentBlockCount = 0

        self.hash = hashlib.sha256()

        self.committedTransactions = []
        self.pendingTransactions = []
        self.pendingTransactionsToRemove = []

        self.waitingForPuzzle = False
        self.waitingForBlockChain = False
        self.numBlocksToWaitFor = 0

        self.waitingForBlockChainFrom = None

        self.minTransactionsBeforeHash = 3
        self.maxTransactionsBeforeHash = 8
        self.numTransactionsBeforeHash = random.randint(self.minTransactionsBeforeHash, self.maxTransactionsBeforeHash)

#############


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
        if (transaction in self.pendingTransactions):
            self.pendingTransactionsToRemove.append(transaction)

        self.currentBlockCount += 1
        if(self.currentBlock.transactionCount == self.numTransactionsBeforeHash):
            blockHash = self.hashCurrentBlock()
            self.currentBlockCount = 0
            self.numTransactionsBeforeHash = random.randint(self.minTransactionsBeforeHash, self.maxTransactionsBeforeHash)
            self.waitingForPuzzle = True

    def appendPendingTransactionsToNewBlock(self):
        print("\tappendPendingTransactionsToNewBlock()")
        for pt in self.pendingTransactions:
            self.appendTransactionToCurrentBlock(pt)

    def removeAddedTransactionsFromPending(self):
        for transactionToRemove in self.pendingTransactionsToRemove:
            self.pendingTransactions.remove(transactionToRemove)
        self.pendingTransactionsToRemove = []

##############

    def betterBlock(self, ip, port, blockMessage):
        [wordBLOCK, blockString] = blockMessage
        block = self.singleBlockFromMessage(blockString)

        if(block.level > self.blockLevel):

            # set level so other blocks don't interfere
            self.blockLevel = block.level
            if(self.currentBlock is not None):
                for transaction in self.currentBlock.getTransactions():
                    self.appendTransactionsToPending(transaction)
                if (block.previousBlockHash == self.lastSuccessfulHash):
                    # Create new block
                    self.currentBlock = Block(level=(self.blockLevel+1), previousHash=block.previousBlockHash)
                    # Move pending transactions to it
                    self.appendPendingTransactionsToNewBlock()
                    self.removeAddedTransactionsFromPending()
                    # Update stuff
                    self.lastSuccessfulHash = block.selfHash
                    self.lastSuccessfulBlock = copy.deepcopy(block)

                    return False

                else:
                    self.obsoleteHashes += [self.currentBlock.selfHash]

            self.blockchain = dict()
            self.currentBlock = None
            self.lastSuccessfulHash = None
            self.lastSuccessfulBlock = None
            self.waitingForBlockChain = True

            self.waitingForBlockChainFrom = (ip, port)

            self.numBlocksToWaitFor = block.level
            self.committedTransactions = []

            return True

        return False

##############

    def successfulBlock(self, message):
        [wordBLOCK, hashOfBlock, puzzleAnswer] = message
        #print("BLOCK MANAGER currentHash: " + str(self.currentHash))
        #print("BLOCK MANAGER currentBlock.selfHash: " + str(self.currentBlock.selfHash))
        #print("BLOCK MANAGER hashOfBlock: " + str(hashOfBlock))
        if(self.currentBlock is not None):
            if(self.currentBlock.selfHash == hashOfBlock):
                #print("BLOCK SUCCESS")
                self.blockLevel = self.currentBlock.level
                self.currentBlock.puzzleAnswer = puzzleAnswer
                self.blockchain[self.currentBlock.level, hashOfBlock] = copy.deepcopy(self.currentBlock)
                self.lastSuccessfulHash = hashOfBlock
                self.waitingForPuzzle = False
                return True
        return False

    def newBlock(self):
        #print("newBlock()")
        previousLevel = self.currentBlock.level
        previousHash = self.currentBlock.selfHash
        self.lastSuccessfulBlock = copy.deepcopy(self.currentBlock)
        self.currentBlock = Block(level=(previousLevel + 1), previousHash=previousHash)

    def fillNewBlock(self):
        #print("fillNewBlock()")
        self.appendPendingTransactionsToNewBlock()
        self.removeAddedTransactionsFromPending()

###### Messages to Blocks #####

    def buildChain(self, message):
        wordBLOCKCHAIN, blockString = message
        block = self.singleBlockFromMessage(blockString)
        self.blockchain[block.level, block.selfHash] = block
        if(block.level == self.blockLevel):
            self.waitingForBlockChain = False
            self.clearPendingTransactionsOnBlockChain()

    def clearPendingTransactionsOnBlockChain(self):
        for block in self.blockchain.values():
            for transaction in block.getTransactions():
                if(transaction in self.pendingTransactions):
                    self.pendingTransactions.remove(transaction)

    def singleBlockFromMessage(self, byteString):

        hash, level, content = byteString.split("$")
        block = Block(level=level, previousHash=hash)

        for transaction in content.split("*"):
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

