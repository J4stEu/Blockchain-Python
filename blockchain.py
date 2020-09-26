import hashlib
from datetime import datetime
from app import db
from models import *

class Block(object):
    def __init__(self, timeStamp, transactions, prevHash, hash, nonce):
        self.timeStamp = timeStamp
        self.transactions = transactions
        self.prevHash = prevHash
        self.hash = hash
        self.nonce = nonce

class Transaction(object):
    def __init__(self, id, vIn, vOut):
        self.id = id
        self.vIn = vIn
        self.vOut = vOut

class TransactionOutput(object):
    def __init__(self, val, pubKey):
        self.val = val
        self.pubKey = pubKey
    
    def canBeUnlockedWith(self, unlockingData):
        return self.pubKey == unlockingData

class TransactionInput(object):
    def __init__(self, id, vOut, sig):
        self.id = id
        self.vOut = vOut
        self.sig = sig

    def canUnlockOutputWith(self, unlockingData):
        return self.sig == unlockingData

class Chain(object):
    def __init__(self):
        self.blocks = []
        #self.targetBits = int(24)
        self.targetBits = int(12)
        self.signUnit = 1

    def proofOfWork(self, block):
        #256 битов имеет хеш. 256(бит) - цель(бит): сложность. При делении на 4 получаем представление сложности (10000...000) в 16-й системе. Путем перевода из 16-й в 10-ю получаем сложность в 10-й.
        target = int(str(int(10**round((256 - self.targetBits)/4))), 16) #Из за цели в 24 бита, получаем сложность в 29 байт (256 - 24 = 232. 232/8 = 29).
        maxInt64 = int(9223372036854775807) #64 бита(8 байт), чтобы не уйти в переполнение(маловероятно)
        nonce = 0
        allIdsTxsInOne = ''
        for tx in block.transactions:
            allIdsTxsInOne += tx.id
        txHash = hashlib.sha256(allIdsTxsInOne.encode('utf-8')).hexdigest()
        while nonce < maxInt64:
            allInOne = str(block.timeStamp) + str(txHash) + str(block.prevHash) + '{:x}'.format(int(nonce))
            dataHash = hashlib.sha256(allInOne.encode('utf-8')).hexdigest()
            if ((int(dataHash, 16) > target) - (int(dataHash, 16) < target)) == -1:
                break
            else: 
                #print('{:x}'.format(int(nonce)))
                nonce+=1

        return dataHash, nonce
    
    def blockProofCheck(self, block):
        target = int(str(int(10**round((256 - self.targetBits)/4))), 16)
        allInOne = str(block.timeStamp) + str(block.data) + str(block.prevHash) + '{:x}'.format(int(block.nonce))
        dataHash = hashlib.sha256(allInOne.encode('utf-8')).hexdigest()
        return ((int(dataHash, 16) > target) - (int(dataHash, 16) < target)) == -1
        
    def proofCheck(self):
        print('Proof of work verification:', sep='\n')
        print('', sep='\n')
        blocks = Blocks.query.all()
        #for block in self.blocks:
        for block in blocks:
            print('Data: ' + block.data, sep='\n')
            print('Hash: ' + block.hash, sep='\n')
            print('Pr.hash: ' + block.prevHash, sep='\n')
            print('Proof of work: ' + 'valid' if self.blockProofCheck(Block(block.timeStamp, block.data, block.prevHash, block.hash, block.nonce)) else 'invalid')
            print(sep='\n')

    def setHash(self, block):
        allInOne = str(block.timeStamp) + str(block.transactions) + str(block.prevHash) + '{:x}'.format(int(block.nonce))
        return hashlib.sha256(allInOne.encode('utf-8')).hexdigest()

    def newBlock(self, transactions, prevHash):
        block = Block(datetime.now(), transactions, prevHash, '', '')
        #block = Block('now', data, prevHash, '')
        block.hash, block.nonce = self.proofOfWork(block)
        #block.hash = self.setHash(block)
        return block
    
    def transactionHash(self, transaction):
        for i in range(len(transaction.vIn)):
            allInOne = str(transaction.vIn[i].id) + str(transaction.vIn[i].vOut) + str(transaction.vIn[i].sig)
            allInOne += str(transaction.vOut[i].val) + str(transaction.vOut[i].pubKey)
        txHash = hashlib.sha256(allInOne.encode('utf-8')).hexdigest()
        return txHash

    def newTransaction(self, to, data):
        if str(data) == '':
            data = 'Rewards to ' + str(to) + '\'s for mining the Genesis Block'
        tIn = TransactionInput(None, -1, data)
        tOut = TransactionOutput(self.signUnit, to)
        tr = Transaction(0, [tIn], [tOut])
        tr.id = self.transactionHash(tr)
        return tr

    def unspentTxs(self, address):
        unspentTxs = []
        #unlockingInputs = []
        for block in self.blocks:
            for tx in block.transactions:
                for index, vOut in enumerate(tx.vOut):
                    move = True
                    for vIn in tx.vIn:
                        if (index == vIn.vOut):
                            move = False
                            break
                    if move == False: continue
                    if vOut.canBeUnlockedWith(address):
                        unspentTxs.append(vOut)

                #for vIn in tx.vIn:
                    #if vIn.vOut == -1: break #first transaction
                    #if vIn.canUnlockOutputWith(address):
                        #unlockingInputs.append(vIn)
                        #break

        return unspentTxs
    
    def getBalance(self, address):
        balance = 0
        for tx in self.unspentTxs(address):
            balance += int(tx.val)
        print('Balance of ' + address + ': ' + str(balance))
        pass
    
    class TransactionOutput(object):
        def __init__(self, val, pubKey):
            self.val = val
            self.pubKey = pubKey
        
        def canBeUnlockedWith(self, unlockingData):
            return self.pubKey == unlockingData

    class TransactionInput(object):
        def __init__(self, id, vOut, sig):
            self.id = id
            self.vOut = vOut
            self.sig = sig

        def canUnlockOutputWith(self, unlockingData):
            return self.sig == unlockingData

    def genesisBlock(self, to, data):
        transactions = [self.newTransaction(to, data)]
        return self.newBlock(transactions, '')

    #def addBlock(self, to, data):
        #transaction = self.newTransaction(to, data)
        #prevBlock = self.blocks[len(self.blocks) - 1]
        #print('Mining the block with data "' + str(transaction) + '"...', sep='\n')
        #last = Last.query.first()
        #prevBlock = Blocks.query.filter(Blocks.id == last.last_block_id).all()

        #newBlock = self.newBlock(data, self.setHash(Block(prevBlock[0].timeStamp, prevBlock[0].data, prevBlock[0].prevHash, prevBlock[0].hash, prevBlock[0].nonce)))

        #block = Blocks(timeStamp = str(newBlock.timeStamp), data = str(newBlock.transactions), prevHash = str(newBlock.prevHash), hash = str(newBlock.hash), nonce = str(newBlock.nonce))
        #db.session.add(block)

        #last.last_block_id = Blocks.query.count() + 1
        #last.last_block_hash = str(newBlock.hash)

        #db.session.commit()
        #print('Sucess.', sep='\n')

        #self.blocks.append(newBlock)

    def addBlock(self, to, data):
        transaction = self.newTransaction(to, data)
        prevBlock = self.blocks[len(self.blocks) - 1]
        #print('Mining the block with data "' + str(transaction) + '"...', sep='\n')
        print('Mining the block...', sep='\n')

        newBlock = self.newBlock(data, self.setHash(Block(prevBlock.timeStamp, prevBlock.transactions, prevBlock.prevHash, prevBlock.hash, prevBlock.nonce)))

        print('Sucess.', sep='\n')

        self.blocks.append(newBlock)
    
    def showBlocks(self):
        print('All blocks:', sep='\n')
        print('', sep='\n')
        blocks = Blocks.query.all()
        #for block in self.blocks:
        for block in blocks:
            print('Data: ' + block.data, sep='\n')
            print('Hash: ' + block.hash, sep='\n')
            print('Pr.hash: ' + block.prevHash, sep='\n')
            print(sep='\n')

class BlockChain(Chain):
    def __init__(self):
        super(BlockChain, self).__init__()
        blocks = Blocks.query.count()
        if (int(blocks) == 0):
            print('There is no blockchain yet. Creating...', sep='\n')
            print('Mining the block with data "Genesis block"...', sep='\n')
            #GB = self.genesisBlock()
            #block = Blocks(timeStamp = str(GB.timeStamp), data = str(GB.transactions), prevHash = str(GB.prevHash), hash = str(GB.hash), nonce = str(GB.nonce))
            #db.session.add(block)
            
            #last = Last(last_block_id = 1, last_block_hash = str(GB.hash))
            #db.session.add(block)

            #db.session.commit()
            #print('Sucess.', sep='\n')

            #self.blocks.append(self.genesisBlock())
    
class newBlockChain(Chain):
    def __init__(self, to, data = ''):
        super(newBlockChain, self).__init__()
        print('There is no blockchain yet. Creating...', sep='\n')
        print('Mining the block with data "Genesis block"...', sep='\n')
        GB = self.genesisBlock(to, data)
        self.blocks.append(GB)
        print('Sucess.', sep='\n')

        #self.blocks.append(self.genesisBlock())