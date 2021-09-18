import hashlib
from datetime import datetime
#from app import db
#from models import *

# class Wallet(object):
#     def __init__(self, privateKey, publicKey):
#         self.privateKey = privateKey
#         self.publicKey = publicKey
#
# class Wallets(object):
#     def __init__(self):
#         self.wallets = []
#
#     def newWallet(self):
#         # prKey, pubKey = newKeyPair()
#         pass
#
#     def newKeyPair(self):
#         pass

# Single block itself
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

# Instance that consists of blocks
class Chain(object):
    def __init__(self):
        self.blocks = []
        # We can change target bits due to control complexity of making new blocks
        #self.targetBits = int(24)
        self.targetBits = int(12)
        self.signUnit = 10

    # hash - 256 bits
    # target bits - 25 bits -> target instance that is smaller than the hash (not valid proof of work)
    # we need to calculate new hash(for new block) with (nonce + new block info) to be smaller than target instance
    def proofOfWork(self, block):
        target = int(str(int(10**round((256 - self.targetBits)/4))), 16) # target bits -> target instance
        maxInt64 = int(9223372036854775807) # 64 bits (8 bytes). To prevent overflow
        nonce = 0
        allIdsTxsInOne = ''
        for tx in block.transactions:
            allIdsTxsInOne += tx.id
        txHash = hashlib.sha256(allIdsTxsInOne.encode('utf-8')).hexdigest()
        while nonce < maxInt64:
            allInOne = str(block.timeStamp) + str(txHash) + str(block.prevHash) + '{:x}'.format(int(nonce))
            dataHash = hashlib.sha256(allInOne.encode('utf-8')).hexdigest()
            if ((int(dataHash, 16) > target) - (int(dataHash, 16) < target)) == -1: # cmp
                break
            else:
                #print('{:x}'.format(int(nonce)))
                nonce += 1

        return dataHash, nonce

    # check if proof of work is valid for a single block
    def blockProofCheck(self, block):
        target = int(str(int(10**round((256 - self.targetBits)/4))), 16)
        allInOne = str(block.timeStamp) + str(block.data) + str(block.prevHash) + '{:x}'.format(int(block.nonce))
        dataHash = hashlib.sha256(allInOne.encode('utf-8')).hexdigest()

        return ((int(dataHash, 16) > target) - (int(dataHash, 16) < target)) == -1

    def proofCheck(self):
        # print('Proof of work verification:', sep='\n')
        # print('', sep='\n')

        #blocks = Blocks.query.all()
        #for block in blocks:
        for block in self.blocks:
            print('Data: ' + block.data)
            print('Hash: ' + block.hash)
            print('Pr.hash: ' + block.prevHash)
            print('Proof of work: ' + 'valid' if self.blockProofCheck(Block(block.timeStamp, block.data, block.prevHash, block.hash, block.nonce)) else 'invalid')
            print('\n')

    def setHash(self, block):
        allIdsTxsInOne = ''
        for tx in block.transactions:
            allIdsTxsInOne += tx.id
        txHash = hashlib.sha256(allIdsTxsInOne.encode('utf-8')).hexdigest()
        allInOne = str(block.timeStamp) + str(txHash) + str(block.prevHash) + '{:x}'.format(int(block.nonce))

        return hashlib.sha256(allInOne.encode('utf-8')).hexdigest()

    def newBlock(self, transactions, prevHash):
        block = Block(datetime.now(), transactions, prevHash, '', '')
        block.hash, block.nonce = self.proofOfWork(block)

        return block

    def transactionHash(self, transaction):
        allInOne = ''
        for txIn in transaction.vIn:
            allInOne += str(txIn.id) + str(txIn.vOut) + str(txIn.sig)
        for txOut in transaction.vOut:
            allInOne += str(txOut.val) + str(txOut.pubKey)
        txHash = hashlib.sha256(allInOne.encode('utf-8')).hexdigest()

        return txHash

    def coinBaseTx(self, to, data):
        if str(data) == '':
            data = 'Rewards to ' + str(to) + '\'s for mining Genesis Block'
        tIn = TransactionInput(None, -1, data)
        tOut = TransactionOutput(self.signUnit, to)
        tr = Transaction(0, [tIn], [tOut])
        tr.id = self.transactionHash(tr)

        return tr

    def unspentTxs(self, address):
        unspentTxs = []
        unlockingInputs = []
        unspentValidTxs = []
        for block in self.blocks:
            for tx in block.transactions:
                for index, vOut in enumerate(tx.vOut):
                    move = True
                    for vIn in tx.vIn:
                        # if an input have any reference to the output -> tx was spent
                        if (index == vIn.vOut) and (vIn.id == tx.id):
                            move = False
                            break
                    if move == False: continue
                    if vOut.canBeUnlockedWith(address):
                        # set tx itself, index of the vOut and vOut itself
                        unspentTxs.append([tx, index, vOut])
                # print('Len vIn:' + str(len(tx.vIn)))
                for vIn in tx.vIn:
                    if vIn.vOut == -1: break # first transaction
                    if vIn.canUnlockOutputWith(address):
                        unlockingInputs.append(vIn)

        # print('Outputs', sep='\n')
        # for tx in unspentTxs:
        #     print('Tx id:' + tx[0].id, sep='\n')
        #     print('Output id:' + str(tx[1]), sep='\n')
        #     print('Output val:' + str(tx[2].val), sep='\n')
        #     print('Output key:' + tx[2].pubKey, sep='\n')
        #     print('', sep='\n')
        # print('', sep='\n')
        # print('Inputs', sep='\n')
        # for tx in unlockingInputs:
        #     print('Tx id:' + str(tx.id), sep='\n')
        #     print('Input output id:' + str(tx.vOut), sep='\n')
        #     print('Input user:' + tx.sig, sep='\n')
        #     print('', sep='\n')

        # we have unlocking inputs and unspent transactions -> get valid unspent transactions
        if len(unlockingInputs) == 0:
            unspentValidTxs = unspentTxs
        else:
            for vOutput in unspentTxs:
                for vInput in unlockingInputs:
                    equals = False
                    for vInput in unlockingInputs:
                        if (vInput.id == vOutput[0].id) and (vInput.vOut == vOutput[1]):
                            equals = True
                            break
                    if equals == False:
                        unspentValidTxs.append(vOutput)
                        break

        return unspentValidTxs

    def getBalance(self, address):
        balance = 0
        for tx in self.unspentTxs(address):
            #print(tx[2].val)
            balance += int(tx[2].val)
        print('Balance of ' + address + ': ' + str(balance))

    def accVer(self, address, amount):
        unspentTxs = self.unspentTxs(address)
        unspentAddressTxs = []
        acc = 0
        for tx in unspentTxs:
            if tx[0].vOut[tx[1]].canBeUnlockedWith(address) and (acc < amount):
                acc += tx[2].val
                unspentAddressTxs.append(tx)
                if (acc >= amount): break

        return acc, unspentAddressTxs

    def newTransaction(self, fr, to, amount):
        inputs = []
        outputs = []
        acc, unspentAddressTxs = self.accVer(fr, amount)

        if acc < amount:
            print('Not enough units...')
            return
        # print('Acc:' + str(acc))

        for tx in unspentAddressTxs:
            inputs.append(TransactionInput(tx[0].id, tx[1], fr))

        outputs.append(TransactionOutput(amount, to))
        if acc > amount:
            outputs.append(TransactionOutput(acc - amount, fr))

        tx = Transaction(None, inputs, outputs)
        tx.id = self.transactionHash(tx)

        return tx

    def genesisBlock(self, to, data):
        transactions = [self.coinBaseTx(to, data)]
        print('Sucess.')
        return self.newBlock(transactions, '')

    # def addBlock(self, to, data):
    #     transaction = self.coinBaseTx(to, data)
    #     prevBlock = self.blocks[len(self.blocks) - 1]
    #     print('Mining the block with data "' + str(transaction) + '"...', sep='\n')
    #     last = Last.query.first()
    #     prevBlock = Blocks.query.filter(Blocks.id == last.last_block_id).all()

    #     newBlock = self.newBlock(data, self.setHash(Block(prevBlock[0].timeStamp, prevBlock[0].data, prevBlock[0].prevHash, prevBlock[0].hash, prevBlock[0].nonce)))

    #     block = Blocks(timeStamp = str(newBlock.timeStamp), data = str(newBlock.transactions), prevHash = str(newBlock.prevHash), hash = str(newBlock.hash), nonce = str(newBlock.nonce))
    #     db.session.add(block)

    #     last.last_block_id = Blocks.query.count() + 1
    #     last.last_block_hash = str(newBlock.hash)

    #     db.session.commit()
    #     print('Sucess.', sep='\n')

    #     self.blocks.append(newBlock)

    def addBlock(self, transactions):
        prevBlock = self.blocks[len(self.blocks) - 1]
        #transaction = self.newTransaction(fr, to, amount)
        #print('Mining the block with data "' + str(transaction) + '"...', sep='\n')
        print('Mining the block...')
        newBlock = self.newBlock(transactions, self.setHash(Block(prevBlock.timeStamp, prevBlock.transactions, prevBlock.prevHash, prevBlock.hash, prevBlock.nonce)))
        self.blocks.append(newBlock)

    def send(self, fr, to, amount):
        print('Sending data=' + str(amount) + ' from ' + fr + ' to ' + to)
        # here should be all new transactions.
        transaction = self.newTransaction(fr, to, amount)
        if transaction:
            self.addBlock([transaction])
            print('Sucess.')

    def showBlocks(self):
        print('All blocks:')
        print('\n')
        #blocks = Blocks.query.all()
        #for block in blocks:
        for index, block in enumerate(self.blocks):
            print('Block Id: ' + str(index))
            print('Hash: ' + block.hash)
            print('Nonce: ' + str(block.nonce))
            print('Pr.hash: %s' % (block.prevHash if block.prevHash else 'none'))
            print('Time: ' + str(block.timeStamp))
            print('Transactions(count): ' + str(len(block.transactions)))
            for index, transaction in enumerate(block.transactions):
                print(' - Transaction ' + str(index + 1))
                print(' - Transaction id:' + str(transaction.id))
                print(' - Inputs (count):' + str(len(transaction.vIn)))
                print(' - Outputs (count):' + str(len(transaction.vOut)))
                for vInIndex, vIn in enumerate(transaction.vIn):
                    print(' -> Input ' + str(vInIndex))
                    print(' -> Input id:' + str(vIn.id))
                    print(' -> Input sig:' + vIn.sig)
                    print(' -> Relative id of output:' + str(vIn.vOut))

                for vOutIndex, vOut in enumerate(transaction.vOut):
                    print(' -> Output ' + str(vOutIndex))
                    print(' -> Output public key:' + vOut.pubKey)
                    print(' -> Output value:' + str(vOut.val))
            print('\n')
            # print('Transactions data: ' + trData)

# DB is working mode
# class BlockChain(Chain):
#     def __init__(self):
#         super(BlockChain, self).__init__()
#         blocks = Blocks.query.count()
#         if (int(blocks) == 0):
#             print('There is no blockchain instance yet. Creating...')
            # print('Mining the block with data "Genesis block"...', sep='\n')
            # GB = self.genesisBlock()
            # block = Blocks(timeStamp = str(GB.timeStamp), data = str(GB.transactions), prevHash = str(GB.prevHash), hash = str(GB.hash), nonce = str(GB.nonce))
            # db.session.add(block)

            # last = Last(last_block_id = 1, last_block_hash = str(GB.hash))
            # db.session.add(block)

            # db.session.commit()
            # print('Sucess.', sep='\n')

            # self.blocks.append(self.genesisBlock())

# DB is not wirking mode
class newBlockChain(Chain):
    def __init__(self, to, data = ''):
        super(newBlockChain, self).__init__()
        print('There is no blockchain instance yet. Creating...')
        print('Mining the block with data "Genesis block"...')
        Gb = self.genesisBlock(to, data)
        self.blocks.append(Gb)

print('\n')
print('Example: ')
print('\n')
bc = newBlockChain('Eugene')
print('\n')
bc.send('Eugene', 'Ivan', 6)
bc.getBalance('Eugene')
print('\n')
bc.send('Eugene', 'Ivan', 2)
bc.getBalance('Eugene')
print('\n')
bc.send('Eugene', 'Ivan', 2)
bc.getBalance('Eugene')
print('\n')
bc.send('Ivan', 'Eugene', 7)
bc.getBalance('Ivan')
print('\n')
bc.getBalance('Eugene')
bc.getBalance('Ivan')
print('\n')
bc.send('Ivan', 'Eugene', 7)
bc.getBalance('Ivan')
print('\n')
bc.showBlocks()
