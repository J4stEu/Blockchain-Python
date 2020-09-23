import hashlib
from datetime import datetime
from app import db
from models import *

class Block(object):
    def __init__(self, timeStamp, data, prevHash, hash, nonce):
        self.timeStamp = timeStamp
        self.data = data
        self.prevHash = prevHash
        self.hash = hash
        self.nonce = nonce

class Chain(object):
    def __init__(self):
        #self.blocks = []
        #self.targetBits = int(24)
        self.targetBits = int(12)
        self.signUnit = 1


    def proofOfWork(self, block):
        #256 битов имеет хеш. 256(бит) - цель(бит): сложность. При делении на 4 получаем представление сложности (10000...000) в 16-й системе. Путем перевода из 16-й в 10-ю получаем сложность в 10-й.
        target = int(str(int(10**round((256 - self.targetBits)/4))), 16) #Из за цели в 24 бита, получаем сложность в 29 байт (256 - 24 = 232. 232/8 = 29).
        maxInt64 = int(9223372036854775807) #64 бита(8 байт), чтобы не уйти в переполнение(маловероятно)
        nonce = 0
        while nonce < maxInt64:
            allInOne = str(block.timeStamp) + str(block.data) + str(block.prevHash) + '{:x}'.format(int(nonce))
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
        allInOne = str(block.timeStamp) + str(block.data) + str(block.prevHash) + '{:x}'.format(int(block.nonce))
        return hashlib.sha256(allInOne.encode('utf-8')).hexdigest()

    def newBlock(self, data, prevHash):
        block = Block(datetime.now(), data, prevHash, '', '')
        #block = Block('now', data, prevHash, '')
        block.hash, block.nonce = self.proofOfWork(block)
        #block.hash = self.setHash(block)
        return block
    
    def genesisBlock(self):
        return self.newBlock('Genesis block', '')

    def addBlock(self, data):
        #prevBlock = self.blocks[len(self.blocks) - 1]
        print('Mining the block with data "' + str(data) + '"...', sep='\n')
        last = Last.query.first()
        prevBlock = Blocks.query.filter(Blocks.id == last.last_block_id).all()

        newBlock = self.newBlock(data, self.setHash(Block(prevBlock[0].timeStamp, prevBlock[0].data, prevBlock[0].prevHash, prevBlock[0].hash, prevBlock[0].nonce)))

        block = Blocks(timeStamp = str(newBlock.timeStamp), data = str(newBlock.data), prevHash = str(newBlock.prevHash), hash = str(newBlock.hash), nonce = str(newBlock.nonce))
        db.session.add(block)

        last.last_block_id = Blocks.query.count() + 1
        last.last_block_hash = str(newBlock.hash)

        db.session.commit()
        print('Sucess.', sep='\n')

        #self.blocks.append(newBlock)
    
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
            GB = self.genesisBlock()
            block = Blocks(timeStamp = str(GB.timeStamp), data = str(GB.data), prevHash = str(GB.prevHash), hash = str(GB.hash), nonce = str(GB.nonce))
            db.session.add(block)
            
            last = Last(last_block_id = 1, last_block_hash = str(GB.hash))
            db.session.add(block)

            db.session.commit()
            print('Sucess.', sep='\n')

            #self.blocks.append(self.genesisBlock())