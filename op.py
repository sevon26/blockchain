import pymongo

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
db = myclient["blockchainDB"]
col_bk = db['blocks']
chain_01 = db['chain_01']
chain_02 = db['chain_02']
chain_03 = db['chain_03']
txpool = db['txpool']

def showTable(collection):
    print(collection, ' :\n')
    if db[collection].find_one() == None:
        print('Empty')
    else:
        for doc in db[collection].find():
            print(doc)

def deleteTables(collection):
    print('deleted: ', collection)
    db[collection].delete_many({})
        
def showAllTable():
    for col in db.collection_names():
        showTable(col)
        print('\n')
def deleteAllTables():
    for col in db.collection_names():
        deleteTables(col)

def insert():
    Tx1 = input('First transaction: ')
    Tx2 = input('Second transaction: ')
    if Tx1 =='' and Tx2 =='':
        print('Please give at least one input.')
    elif Tx1 =='' or Tx2 =='':
        print('Successfully inserted ', Tx1, ' ', Tx2, '\n')
    else :
        print('Successfully inserted ', Tx1, ' and ', Tx2, '\n')
    txpool.insert_one({'transaction1':Tx1, 'transaction2':Tx2})

print('db: col_bk   chain_01    chain_02    chain_03    txpool')
print('op: show all  insert   del all     show (col)     del(col)')
while 1:
    op = input('Operation: ')
    if op == 'show all':    showAllTable()
    elif op == 'del all':   deleteAllTables()

    elif op == 'show col_bk': showTable(col_bk)
    elif op == 'show chain_01': showTable(chain_01)
    elif op == 'show chain_02': showTable(chain_02)
    elif op == 'show chain_03': showTable(chain_03)
    elif op == 'show txpool': showTable(txpool)
    
    elif op == 'del col_bk': deleteTables(col_bk)
    elif op == 'del chain_01': deleteTables(chain_01)
    elif op == 'del chain_02': deleteTables(chain_02)
    elif op == 'del chain_03': deleteTables(chain_03)
    elif op == 'del txpool': deleteTables(txpool)

    elif op == 'insert': insert()
