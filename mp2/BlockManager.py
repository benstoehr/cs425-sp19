import hashlib
from block import Block

class BlockManager(object):

    def __init__(self):

        self.blockLevel = 0
        self.bank = dict()

        self.blockchain = dict()

        self.pendingBlocks = []

        self.currentBlock = Block()
        self.currentBlockCount = 0

        self.hash = hashlib.sha256()

        self.pendingTransactions = []
        self.waitingForPuzzle = False

#############
    def hashCurrentBlock(self):
        self.hash.update(self.currentBlockAsString().encode('utf-8'))
        return self.hash.hexdigest()

    def currentBlockAsString(self):
        return self.currentBlock.toMessage()


    # Adds one transaction to the current block, only happens if transaction is possible (no negatives
    def appendTransactionToCurrentBlock(self, transaction):
        self.currentBlock.addTransactionToBlock(transaction)
        self.currentBlockCount += 1
        if(self.currentBlockCount == 10):
            self.currentBlockCount = 0
            self.waitingForPuzzle = True
            return self.hashCurrentBlock()
        else:
            return None


###### Sending STUFF #####

    def singleBlockFromMessage(self, byteString):
        block = Block()
        hash, content = byteString.split("$")
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

