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

        self.minTransactionsBeforeHash = 2
        self.maxTransactionsBeforeHash = 6
        self.numTransactionsBeforeHash = random.randint(self.minTransactionsBeforeHash, self.maxTransactionsBeforeHash)

#############

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
        h = hashlib.sha256().update(self.currentBlockAsString().encode('utf-8'))
        hh = h.hexdigest()
        #self.currentBlock.selfHash = hh
        return hh

    def hashBlockString(self, blockString):
        h = hashlib.sha256().update(blockString.encode('utf-8'))
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

        fromAccount = int(transaction[3])
        toAccount = int(transaction[4])
        amount = int(transaction[5])
        self.addAccounts(fromAccount, toAccount)

        if(self.waitingForPuzzle or self.waitingForBlockChain):
            if (transaction not in self.pendingTransactions):
                #print("\t\tP" + str(transaction))
                self.appendTransactionsToPending(transaction)
            return

        ## TODO: reject the bad transaction
        # TRANSACTION 1551208414.204385 f78480653bf33e3fd700ee8fae89d53064c8dfa6 183 99 10
        tradeExecuted = self.executeTrade(fromAccount, toAccount, amount)
        if(not tradeExecuted):
            #print("\tInvalid:\t" + str(transaction))
            return

        #print("\t" + str(transaction))
        self.currentBlock.addTransactionToBlock(transaction)
        if (transaction in self.pendingTransactions):
            self.pendingTransactionsToRemove.append(transaction)
        self.currentBlockCount += 1

        if(self.currentBlock.transactionCount == self.numTransactionsBeforeHash):
            print("\n~~~~~~~MAKING NEW HASH~~~~~~~~\n")
            blockHash = self.hashCurrentBlock()
            self.currentBlock.selfHash = blockHash
            self.numTransactionsBeforeHash = random.randint(self.minTransactionsBeforeHash, self.maxTransactionsBeforeHash)
            self.waitingForPuzzle = True

    def appendPendingTransactionsToNewBlock(self):
        #print("\tappendPendingTransactionsToNewBlock()")
        for pt in self.pendingTransactions:
            self.appendTransactionToCurrentBlock(pt)


    def removeAddedTransactionsFromPending(self):
        for transactionToRemove in self.pendingTransactionsToRemove:
            if(transactionToRemove in self.pendingTransactions):
                self.pendingTransactions.remove(transactionToRemove)
        self.pendingTransactionsToRemove = []

##############

    def betterBlock(self, ip, port, blockMessage):

        [wordBLOCK, blockString] = blockMessage
        block = self.singleBlockFromMessage(blockString)

        if(block.level > self.blockLevel):
            print("New block has higher level!" + str(block.level))
            block.printSelf()

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

                    # Create new block
                    self.currentBlock = copy.deepcopy(block)
                    # Move pending transactions to it
                    self.clearPendingTransactionsOnBlockChain()
                    self.removeAddedTransactionsFromPending()
                    self.newBlock()
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
        print("BLOCK MANAGER currentBlock.selfHash: " + str(self.currentBlock.selfHash))
        print("BLOCK MANAGER hashOfBlock: " + str(hashOfBlock))
        if(self.currentBlock is not None):
            if(self.currentBlock.selfHash == hashOfBlock):
                print("CONSECUTIVE BLOCK SUCCESS")

                self.blockLevel = self.currentBlock.level
                self.currentBlock.puzzleAnswer = puzzleAnswer
                self.blockchain[self.currentBlock.level] = (hashOfBlock, copy.deepcopy(self.currentBlock))
                self.blockchainBySelfHash[hashOfBlock] = copy.deepcopy(self.currentBlock)
                #self.lastSuccessfulHash = hashOfBlock
                self.newBlock()

                self.fillNewBlock()
                self.waitingForPuzzle = False

                return True

        return False

    def newBlock(self):
        print("newBlock()")
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
        block.printSelf()

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
            self.rebuildBank()
            self.clearPendingTransactionsOnBlockChain()
            self.removeAddedTransactionsFromPending()
            self.newBlock()
            self.fillNewBlock()

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
        print("singleBlock hash")

        h = self.hashBlockString(newBlock.toMessage())
        print(h)
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

