# -*- coding: utf-8 -*-
"""
Created on Mon Nov 26 21:58:33 2018

@author: Administrator
"""

#   server
import socket
import threading
import time
import blockchain as bc 
import json
import pymongo

HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
my_PORT = 8001        # Port to listen on (non-privileged ports are > 1023)
other_PORT = [8002, 8003]        # The port used by the server
bc.CHECK_MINE_01 = 0

myclient = pymongo.MongoClient("mongodb://localhost:27017/")# hy-m{add: for connecting database client}
db = myclient["blockchainDB"] #hy-m{add: for creating database}
col_bk = db['blocks'] #hy-m{add: creating collection(table) in database to store blocks}
chain = db['chain_01']
txpool = db['txpool']

def checkHash(data):
    for item in chain.find():
        if data == item['Hash']:
            return 0
    return 1

def waitForConnection():
    while 1:
        print('(8001) listening for connection...')
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((HOST, my_PORT))
            s.listen()
            conn, addr = s.accept()
            with conn:
                print('****************************Received connection from: ', addr)
                data = conn.recv(1024).decode("utf-8") 
                if data:
                    print('I receive: ', data)
                    if checkHash(data):
                        record = chain.find_one(sort=[("Index", pymongo.DESCENDING)])
                        if record:
                            index = record['Index']
                        else:
                            index = -1
                        chain.insert_one({'Index':index + 1, 'Hash':data})
                        print('Inserted hash value: ', data, ' into the chain')
                        bc.CHECK_MINE_01 = 1    ##############################################################<<<<<<<<<<
                    else:
                        print('The block already exists')
                conn.close()
                print('****************************Connection closed')

t = threading.Thread(target=waitForConnection)
t.start()

print('waiting for transaction...\n')
while 1:
    transactions = txpool.find_one()
    if transactions != None: # if 检测到数据库里存在TX
        bc.CHECK_MINE_01 = 0  ##############################################################<<<<<<<<<<
        print('Found transaction, mining block...\n')
        blockchain_a = bc.BlockChain()
        new_block = blockchain_a.gen_block(transactions) # 对该TX挖矿
        if new_block:   # if 成功挖出来
            if new_block['Nonce'] == 0:    # 被阻断的Block
                time.sleep(1)
                print('Mining is stopped by receiving block from the other node.\n')
            elif checkHash(new_block['Hash']):    # if 不存在于链上
                print('Successfully mined a new block: ', new_block)
                col_bk.insert_one(new_block) # 推上DB 的主blockchain
                chain.insert_one({'Index':new_block['Index'], 'Hash':new_block['Hash']})
                for port in other_PORT: # broadcast
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                        try:
                            conn = s.connect((HOST, port))
                            print('######################Connected to port: ', port, '\n')
                            var = json.dumps(new_block['Hash'])
                            print('Sent block hash to this port: ', var)
                            data = bytes(var, 'utf-8')
                            s.sendall(data)
                            s.close()
                            print('######################Connection closed\n')
                        except:
                            print('failed to connect.\n')
                # after we sent to two ports, delete the tx.
                txpool.delete_one({})
                print('deleted transactions in txpool\n')
            print('waiting for transaction...\n')


