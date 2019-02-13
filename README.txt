Project:
    brief intro:
        In this project, a basic prototype of blockchain has been implemented. 
        This is a simplified Bitcoin system which include some essential components of bitcoin, 
        such as decentralized networking, proof of work algorithm, transaction pool, merkle root, etc.
        The system is written by Python, and MongoDB is involved in our system.

        block prototype:
            block structure:
                1. index
                2. hash
                    return by gen_hash function
                3. pv_hash
                    the hash value of the previous block
                4. nonce
                    a counter used for POW algorithm
                5. timestamp
                    the create time of the block
                6. tx_data
                    a string obtain from user 
                7. merkle root:
                    a hash value for maintaining the originality of the transaction data.
                    return by merkle_root function
                    implementation:
                        get two transactions from transaction pool
                        check whether any input value is empty

                        if there are two non-empty transaction,
                        we add the two string together and hash them with {hashlib.sha256(root.encode()).hexdigest()}

                        if there is only one non-empty transaction, we copy it and add the two same txs together
                        we should first encode the sum string into byte format, 
                        then apply hash function {hashlib.sha256(root.encode())

                8. spendtime
                    the time we need for mining a block

        decentralized networking:
            implementation:
                After each node successfully mined a new block, it will send message
                to neighbor nodes.
                Now let say Node 1 has successfully mined a new block, it has to send
                the block data to node 2. In this situation, Node 2 acts as a server node 
                and Node 1 will be the client node.
                Node 2 will first create a server socket at port 8002 by following python code
                {
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind((HOST, my_PORT))
                }
                then it wait for incoming connection request by code {s.listen()}.

                Client node also create a client socket with the first line of above code.
                Then Node 1 initiates connection to port 8002 by code
                {s.connect((HOST, 8002))}
                After three-way-handshake protocol, a TCP connection will be established.
                
                Now Node 1 can send data to node 2. Before sending data, the data type should be
                encoded into bytes by using utf-8 encoding. Then the data will be sent by the code 
                {s.sendall(data)}. The data Node 1 sent is hash value of the new mined block.

                By using the code {data = conn.recv(1024).decode("utf-8")}, the data is converted 
                back to string, and read by node 2.

                Now the data transfering between 2 nodes is completed. Two nodes will now close the connection
                by using code {s.close()}

        PoW algorithm:
            implementation:
                gen_block() -> mine() -> gen_hash()
                gen_hash() ***
                    return : hash and nonce
                    implementation:
                        for simplification, we set the target value to be 6.
                        the function collects all the information of the block including 
                        index, previous_hash, transaction data, timestamp, merkleroot,
                        and add them together as a string, then apply hash function
                        {hashlib.sha256(var.encode()).hexdigest()}
                        so that we get a string of hash value in hex.
                        we check this string whether it start with 6 zeros.
                        If not, loop the hash process.
                mine()
                    return block
                    usage: initialize a block object, and collect neccesary block information and assign to it.
                gen_block()
                    return block in json format
                    usage: 
                        check whether the block is genesis block. 
                            If true, pv_hash should be 0, pv_id should be -1. *
                            If flase, pv_hash should be the value of previous block's hash value, and pv_id should be the 
                            id of previous block. 
                        Then feed the mine function with pv_id, pv_hash and tx data, 
                        and apply mine function to obtain a block.

        Database:
            5 table:
                1. col_bk: store block information
                2. chain_01: store blockchain copy of node 1
                3. chain_02: store blockchain copy of node 2
                4. chain_03: store blockchain copy of node 3
                5. tx_pool: store transactions given by user
                
            interactions with database:
                get all or any table data from db, and print them out on CLI


    Files:
        1. blockchain.py
            prototype of block, blockchain, definition of mine function, PoW function (gen_hash()), function for finding merkle root.
        2. client01.py
            (port: 8001)
            Implementation of communication between each nodes, each of the client represents a single node. 
            It is responsible for sending and listening request toward other nodes by using socket programming.
            In blockchain, the correctness of the message being sent is very important, it determined the reliability of the system.
            For maintaining the correctness, we use TCP as communication protocol.

            The process contain two threads. The first one helps listening connection request from other nodes. 
            It creates a server socket at port 8001, when the thread receives data form the connection, 
            it will check if there is any same block in its own blockchain. If it is a new block, then insert into 
            the end of the chain and close the connection. Else print out message to remind that it is already exist, 
            and close the connection.

            The second thread do the mining work. If will first continuously check the transaction pool in the database
            if there is any transaction. If transaction exists, the thread start generating new block w.r.t. that transaction.
            Here, the mine function, gen_hash function, gen_block function from blockchain.py are invloved. After successfully 
            mined a new block, the existancy of the block on the chain is being checked before inserting into its own chain.
            After that, the hash value produced by PoW algorithm will be broadcasted by TCP socket to the other nodes. 
            Finally, the transaction in transaction pool can be deleted.

        3. client02.py
            (port: 8002)

        4. client03.py
            (port: 8003)

        5. getTx.py
            This file helps collect transaction messages from users and store them into database. 
            It requests user for two transactions in each loop.

        6. op.py
            This file helps users to perform checking and deleting operations toward database.
            We can easily obtain or delete all records from all collections or any chain of a single node.

    Demo:
        Step 1: 
            Start MongoDB server by using the command: mongod --dbpath <path of the data file>
        Step 2:
            Open 4 new cmds, 3 for each of the 3 clients, 1 for posting transaction messages(getTx.py).
        Step 3:
            Run client01.py, client02.py, client03.py, getTx.py respectively in each cmd.
        Step 4:
            input 2 transactions in op.py
	Step 5:
	    Run op.py to get data from database.

    Packages:
        socket
        threading
        time 
        json
        pymongo
        hashlib
        random