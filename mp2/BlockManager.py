import hashlib
import random
import copy
import time

from block import Block


def sortFunction(x):
    return x[1]

class BlockManager(object):

    def __init__(self, logger):

        self.logger = logger
        self.blockLevel = 0

        self.bank = dict()
        self.committedBank = None

        self.blockchain = dict()

        self.blockchainBySelfHash = dict()

        self.pendingBlocks = []

        self.obsoleteHashes = []

        self.currentBlock = Block(level=1, previousHash="None")

        self.lastSuccessfulHash = "None"
        self.lastSuccessfulBlock = None

        self.currentBlockCount = 0

        self.committedTransactions = []
        self.pendingTransactions = []
        self.pendingTransactionsToRemove = []

        self.waitingForPuzzle = False
        self.waitingForBlockChain = False
        self.numBlocksToWaitFor = 0

        self.waitingForBlockChainFrom = None

        self.minTransactionsBeforeHash = 20
        self.maxTransactionsBeforeHash = 25
        self.numTransactionsBeforeHash = random.randint(self.minTransactionsBeforeHash, self.maxTransactionsBeforeHash)

#############

    def getAccountAccountAmount(self, transaction):
        fromAccount = int(transaction[3])
        toAccount = int(transaction[4])
        amount = int(transaction[5])
        return fromAccount, toAccount, amount

    def addAccounts(self, account1, account2):
        ## ADD THEM TO THE BANK
        if (account1 not in self.bank.keys()):
            self.bank[account1] = 0
        if (account2 not in self.bank.keys()):
            self.bank[account2] = 0

    def executeTrade(self, fromAccount, toAccount, amount):
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
        h = hashlib.sha256()
        h.update(self.currentBlockAsString().encode('utf-8'))
        hh = h.hexdigest()
        #self.currentBlock.selfHash = hh
        return hh

    def hashBlockString(self, blockString):
        h = hashlib.sha256()
        h.update(blockString.encode('utf-8'))
        hh = h.hexdigest()
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


        fromAccount, toAccount, amount = self.getAccountAccountAmount(transaction)
        self.addAccounts(fromAccount, toAccount)

        if(self.waitingForPuzzle or self.waitingForBlockChain):
            if (transaction not in self.pendingTransactions):
                self.appendTransactionsToPending(transaction)
            return

        self.sortPendingTransactions()
        # try to reduce number of invalid by including old
        for pt in self.pendingTransactions[:5]:
            if(pt != transaction):
                # If pending transaction has lower timestamp than most recent one, maybe look at it
                if(pt[1] < transaction[1]):
                    print("RETRY\t\t" + str(pt))
                    fA, tA, a = self.getAccountAccountAmount(pt)
                    self.addAccounts(fA, tA)
                    if(self.executeTrade(fA, tA, a)):
                        self.currentBlock.addTransactionToBlock(pt)
                    self.pendingTransactionsToRemove.append(pt)
        #self.removeAddedTransactionsFromPending()

        ## TODO: reject the bad transaction
        # TRANSACTION 1551208414.204385 f78480653bf33e3fd700ee8fae89d53064c8dfa6 183 99 10
        tradeExecuted = self.executeTrade(fromAccount, toAccount, amount)
        if(not tradeExecuted):
            print("\tInvalid:\t" + str(transaction))
            if(transaction not in self.pendingTransactions):
                self.appendTransactionsToPending(transaction)
            self.removeAddedTransactionsFromPending()
            return

        print("BM:S\t" + str(transaction))
        #print("\t" + str(transaction ))
        self.currentBlock.addTransactionToBlock(transaction)
        if (transaction in self.pendingTransactions):
            self.pendingTransactionsToRemove.append(transaction)

        if(self.currentBlock.transactionCount >= self.numTransactionsBeforeHash):
            print("\n~~~~~~~MAKING NEW HASH~~~~~~~~\n")
            blockHash = self.hashCurrentBlock()
            self.currentBlock.selfHash = blockHash
            self.numTransactionsBeforeHash = random.randint(self.minTransactionsBeforeHash, self.maxTransactionsBeforeHash)
            self.waitingForPuzzle = True
        self.removeAddedTransactionsFromPending()


    def appendPendingTransactionsToNewBlock(self):
        print("\tappendPendingTransactionsToNewBlock()")
        for pt in self.pendingTransactions:
            print(pt)
            self.appendTransactionToCurrentBlock(pt)

    def removeAddedTransactionsFromPending(self):
        for transactionToRemove in self.pendingTransactionsToRemove:
            if(transactionToRemove in self.pendingTransactions):
                self.pendingTransactions.remove(transactionToRemove)
        self.pendingTransactionsToRemove = []

    def printPendingTransactions(self):
        for pt in self.pendingTransactions:
            print(pt)

    def sortPendingTransactions(self):
        #s = set(self.pendingTransactions)
        #self.pendingTransactions = list(s)
        self.pendingTransactions.sort(key=sortFunction)



##############

    def logChain(self):
        logString = "CHAIN "
        logString += str(time.time())
        logString += " "
        logString += str(self.blockLevel)
        logString += " "
        for blockHash, block in self.blockchain.values():
            logString += str(blockHash)
            logString += " "
        self.logger.plainLog(logString)

    def betterBlock(self, ip, port, blockMessage):

        [wordBLOCK, blockString] = blockMessage
        block = self.singleBlockFromMessage(blockString)

        if(block.level > self.blockLevel):
            print("New block has higher level!" + str(block.level))
            #block.printSelf()

            #print("Higher Level previousHash: " + block.previousBlockHash)
            #print("Higher Level selfHash: " + block.selfHash)
            # set level so other blocks don't interfere
            self.blockLevel = block.level

            if(self.currentBlock is not None):
                for transaction in self.currentBlock.getTransactions():
                    self.appendTransactionsToPending(transaction)

                if(block.previousBlockHash == "None"):
                    print("Found First block from friend!")

                if (block.previousBlockHash == self.lastSuccessfulHash):
                    print("CONSECUTIVE BETTER BLOCK SUCCESS")
                    #print("I AM SLOW")

                    self.blockchain[block.level] = (block.selfHash, copy.deepcopy(block))
                    self.blockchainBySelfHash[block.selfHash] = copy.deepcopy(block)
                    self.logChain()

                    # Create new block
                    self.currentBlock = copy.deepcopy(block)
                    # Move pending transactions to it

                    self.clearPendingTransactionsOnBlockChain()
                    self.removeAddedTransactionsFromPending()
                    self.sortPendingTransactions()

                    self.rebuildBank()
                    self.committedBank = copy.deepcopy(self.bank)

                    self.newBlock()
                    self.printPendingTransactions()
                    self.appendPendingTransactionsToNewBlock()


                    print("")
                    return False

                else:
                    self.obsoleteHashes += [self.currentBlock.selfHash]

            ## Reset stuff in anticipation of new chain coming in!
            self.blockchain = dict()
            self.blockchainBySelfHash = dict()
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
        #block = self.singleBlockFromMessage(message)
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
                self.blockchainBySelfHash[hashOfBlock] = copy.deepcopy(self.currentBlock)
                self.logChain()

                self.clearPendingTransactionsOnBlockChain()
                self.removeAddedTransactionsFromPending()
                self.sortPendingTransactions()


                self.rebuildBank()
                self.committedBank = copy.deepcopy(self.bank)

                self.newBlock()
                self.printPendingTransactions()
                self.appendPendingTransactionsToNewBlock()
                self.waitingForPuzzle = False

                return True

        return False

    def newBlock(self):
        #print("newBlock()")
        previousLevel = self.currentBlock.level
        previousHash = self.currentBlock.selfHash
        self.lastSuccessfulHash = copy.deepcopy(self.currentBlock.selfHash)
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
        print("Adding Block to Chain")
        #block.printSelf()

        # Put it in the blockchain variable
        self.blockchain[block.level] = (block.selfHash, copy.deepcopy(block))
        self.blockchainBySelfHash[block.selfHash] = copy.deepcopy(block)
        # At this point, you are done
        if(block.level == self.blockLevel):
            self.waitingForBlockChain = False
            self.waitingForPuzzle = False
            # Set this up so new block pulls the correct one.
            self.currentBlock = block

        # Clean up pending transactions
        if(not self.waitingForBlockChain):
            print("NEW CHAIN COMPLETE!!!")
            self.logChain()

            self.rebuildBank()
            self.committedBank = copy.deepcopy(self.bank)

            self.clearPendingTransactionsOnBlockChain()
            self.removeAddedTransactionsFromPending()
            self.sortPendingTransactions()

            self.newBlock()
            self.appendPendingTransactionsToNewBlock()

    def rebuildBank(self):
        print("[REBUILDING BANK]")
        self.bank = dict()
        for blockHash, block in self.blockchain.values():
            for transaction in block.getTransactions():
                fromAccount = int(transaction[3])
                toAccount = int(transaction[4])
                amount = int(transaction[5])
                self.addAccounts(fromAccount, toAccount)
                self.executeTrade(fromAccount, toAccount, amount)

    # Maybe make this by block for speed
    def clearPendingTransactionsOnBlockChain(self):
        for blockHash, block in self.blockchain.values():
            for transaction in block.getTransactions():
                if(transaction in self.pendingTransactions):
                    self.pendingTransactionsToRemove += [transaction]

###################################################

    def singleBlockFromMessage(self, blockString):

        #print("singleBlockFromMessage()")
        #print(blockString)
        # Remove the end character
        blockString = blockString.strip("^")

        # Split into different parts
        [hash, level, content, puzzle] = blockString.split("$")

        # print("hash: " + str(hash))
        # print("level: " + str(level))
        # print("content: " + str(content))
        # print("puzzle: " + str(puzzle))

        # Create the new block
        newBlock = Block(level=int(level), previousHash=hash, puzzle=puzzle)

        # Add transactions and txIDs
        for transaction in content.split("*"):
            splitTransaction = transaction.split("_")
            newBlock.txIDs.append(splitTransaction[2])
            newBlock.transactions.append(splitTransaction)

        # Get hash of new block
        #print("singleBlock hash")

        h = self.hashBlockString(newBlock.toMessage())
        #print(h)
        newBlock.selfHash = h
        #newBlock.printSelf()

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

