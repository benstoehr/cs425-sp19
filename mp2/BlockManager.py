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

        self.currentBlock = Block(level=1, previousHash="0")

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

    def executeTrade(self, fromAccount, toAccount, amount):

        ## ADD THEM TO THE BANK
        if (fromAccount not in self.bank.keys()):
            self.bank[fromAccount] = 0
        if (toAccount not in self.bank.keys()):
            self.bank[toAccount] = 0

        # GET ACCOUNT BALANCE
        fromAccountValue = self.bank[fromAccount]
        toAccountValue = self.bank[toAccount]

        ## IF IT'S ACCOUNT ZERO THEY'RE GOLDEN
        if (fromAccount == 0):
            self.bank[toAccount] = toAccountValue + amount
            return True

        if(amount > fromAccountValue):
            #print("Invalid Transaction: Not enought funds!")
            return False
        else:
            self.bank[fromAccount] = fromAccountValue - amount
            self.bank[toAccount] = toAccountValue + amount
            return True


    def readIncomingBlockChain(self, message):
        block = self.singleBlockFromMessage(message)

#############

    def hashCurrentBlock(self):
        h = self.hash.update(self.currentBlockAsString().encode('utf-8'))
        hh = self.hash.hexdigest()
        self.currentBlock.selfHash = hh
        return hh

    def hashBlockString(self, blockString):
        h = self.hash.update(blockString.encode('utf-8'))
        hh = self.hash.hexdigest()
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



        ## TODO: reject the bad transaction
        # TRANSACTION 1551208414.204385 f78480653bf33e3fd700ee8fae89d53064c8dfa6 183 99 10
        fromAccount = int(transaction[3])
        toAccount = int(transaction[4])
        amount = int(transaction[5])

        tradeExecuted = self.executeTrade(fromAccount, toAccount, amount)
        if(not tradeExecuted):
            print("\tInvalid:\t" + str(transaction))
            return

        print("\t" + str(transaction))
        self.currentBlock.addTransactionToBlock(transaction)
        if (transaction in self.pendingTransactions):
            self.pendingTransactionsToRemove.append(transaction)
        self.currentBlockCount += 1

        if(self.currentBlock.transactionCount == self.numTransactionsBeforeHash):
            blockHash = self.hashCurrentBlock()
            self.currentBlock.selfHash = blockHash
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
                    print("CONSECUTIVE BLOCK SUCCESS")
                    # Create new block
                    self.currentBlock = Block(level=(self.blockLevel+1), previousHash=block.previousBlockHash)
                    # Move pending transactions to it
                    self.clearPendingTransactionsOnBlockChain()
                    self.removeAddedTransactionsFromPending()
                    self.appendPendingTransactionsToNewBlock()

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
                print("CONSECUTIVE BLOCK SUCCESS")
                self.blockLevel = self.currentBlock.level
                self.currentBlock.puzzleAnswer = puzzleAnswer
                self.blockchain[self.currentBlock.level] = (hashOfBlock, copy.deepcopy(self.currentBlock))
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
        # Get the block
        block = self.singleBlockFromMessage(blockString)
        # Put it in the blockchain variable
        self.blockchain[block.level] = (block.selfHash, copy.deepcopy(block))
        # At this point, you are done
        if(block.level == self.blockLevel):
            self.waitingForBlockChain = False
            self.waitingForPuzzle = False

        # Clean up pending transactions
        if(not self.waitingForBlockChain):
            print("NEW CHAIN COMPLETE!!!")
            self.rebuildBank()
            self.clearPendingTransactionsOnBlockChain()
            self.removeAddedTransactionsFromPending()

    def rebuildBank(self):
        self.bank = dict()
        for blockHash, block in self.blockchain.values():
            for transaction in block.getTransactions():
                fromAccount = int(transaction[3])
                toAccount = int(transaction[4])
                amount = int(transaction[5])
                self.executeTrade(fromAccount, toAccount, amount)

    # Maybe make this by block for speed
    def clearPendingTransactionsOnBlockChain(self):
        for blockHash, block in self.blockchain.values():
            for transaction in block.getTransactions():
                if(transaction in self.pendingTransactions):
                    self.pendingTransactionsToRemove += [transaction]

###################################################
    def singleBlockFromMessage(self, blockString):

        hash, level, content, puzzle = blockString.split("$")
        newBlock = Block(level=int(level), previousHash=hash)

        for transaction in content.split("*"):
            splitTransaction = transaction.split("_")
            newBlock.txIDs.append(splitTransaction[2])
            newBlock.transactions.append(splitTransaction)

        newBlock.selfHash = self.hashBlockString(newBlock.toMessage())

        return newBlock

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

