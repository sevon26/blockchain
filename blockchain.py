import json
import random
import hashlib
import time

from threading import Thread
import pymongo

myclient = pymongo.MongoClient("mongodb://localhost:27017/")                                                
db = myclient["blockchainDB"]                                                 
col_bk = db['blocks']                                                 

CHECK_MINE_01 = 0
CHECK_MINE_02 = 0
CHECK_MINE_03 = 0

class Block(object):    
    def __init__(self):
        self.index = None
        self.hash = None
        self.previous_hash = None
        self.nonce = None
        self.timestamp = None
        self.transaction_data = None
        self.merkleroot = None
        self.spendtime = None
    
    def get_block_info(self):
        block_info = {
            'Index': self.index,
            'Hash': self.hash,
            'Previous_hash': self.previous_hash,
            'Nonce': self.nonce,
            'Timestamp': self.timestamp,
            'Transaction_data': self.transaction_data,
            'merkleroot': self.merkleroot,
            'spendtime': self.spendtime
        }
        return block_info

class Pitman(object):
    
    def mine(self, index, previous_hash, transaction_data):
        begin_time = time.time()
        chain = BlockChain()
        block = Block()

        block.index = index+1                                                 
        block.previous_hash = previous_hash
        block.transaction_data = transaction_data
        block.merkleroot = chain.merkle_root(transaction_data)                                                
        block.hash, block.nonce = self.gen_hash(index+1, previous_hash, transaction_data, block)
        end_time = time.time()       
        spend_time = end_time - begin_time                                                
        block.spendtime = spend_time

        return block

    @staticmethod
    def gen_hash(index, previous_hash, transaction_json, block):
        merkleroot = block.merkleroot
        nonce = random.randrange(1, 99999)
        transaction_data = json.dumps(transaction_json)

        guess = str(index) + previous_hash + str(nonce) + transaction_data + merkleroot

        res = hashlib.sha256(guess.encode()).hexdigest()
        while res[:5] != '00000':                                                  
            if CHECK_MINE_01 == 1 or CHECK_MINE_02 == 1 or CHECK_MINE_03 == 1:
                return 0, 0
            nonce += 1                                                                  
            guess = str(index) + previous_hash + str(nonce) + transaction_data + merkleroot                                                 

            res = hashlib.sha256(guess.encode()).hexdigest()
        block.timestamp = time.time()
        return res, nonce

class MyThread(Thread):                                                
    def __init__(self, target, args=()):
        super(MyThread, self).__init__()
        self.func = target
        self.arg = args

    def run(self):
        self.result = self.func(*self.arg)

    def get_result(self):
        try:
            return self.result
        except Exception as e:
            print('自定义线程获取结果时发生了错误:', e)
            return None

class BlockChain(object):                                                 
    def __init__(self):                                                                                                
        self.pv_hash = None                                                 
        
    def merkle_root(self, transaction_data_temp):                                                 
        tx1 = transaction_data_temp['transaction1']                                                 
        tx2 = transaction_data_temp['transaction2']                                                 
        if (tx1 != '') and (tx2 == ''):
            root = str(tx1) + str(tx1)
            return(hashlib.sha256(root.encode()).hexdigest())
        elif (tx1 == '') and (tx2 != ''):                                                
            root = str(tx2) + str(tx2)
            return(hashlib.sha256(root.encode()).hexdigest())
        else:
            root = str(tx1) + str(tx2)                                                
            return(hashlib.sha256(root.encode()).hexdigest()) 
    
    def gen_block(self, transaction_data_temp):                                                
        
        if col_bk.find_one() == None:                                                 
            tx_data = {'transaction1':'', 'transaction2':''}
            tx_data['transaction1'] = transaction_data_temp['transaction1']
            tx_data['transaction2'] = transaction_data_temp['transaction2']
            pv_hash = '0'                                                 
            pv_id = -1                                                 
            block = Pitman.mine(Pitman, pv_id, pv_hash, tx_data)
            if block:
                return block.get_block_info()
        
        else:
            tx_data = {'transaction1':'', 'transaction2':''}
            tx_data['transaction1'] = transaction_data_temp['transaction1']
            tx_data['transaction2'] = transaction_data_temp['transaction2']
            pv_block = col_bk.find_one(sort=[("Index", pymongo.DESCENDING)])                                                 
            pv_hash = pv_block['Hash']                                                 
            pv_id = pv_block['Index']                                                 
            
            block = Pitman.mine(Pitman, pv_id, pv_hash, tx_data)
            if block:
                return block.get_block_info()
                