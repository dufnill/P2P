import logging
import json

from os.path import exists
from Plot import Plot
from App import App
from Unpacker import Unpacker
from Blind_logic import Blind_logic
from threading import Thread
from neo4j import GraphDatabase
from neo4j.exceptions import ServiceUnavailable

"""
This program is used to perform an analisis on some Bitcoin transaction, given in csv format.
I used Neo4j to create a graph database with node of type (Transaction, Block, Input, Output, User)

The relationships between nodes are as follow:

############
- (Input -> Transaction) input that appear in a transaction
- (Input -> Output) inputs that appear in the same transaction where an output appears

- (Output -> Transaction) output that appear in a transaction
- (Output -> Input) output used as input (different transactions)
- (Output -> User) output directed to an user

- (Transaction -> Block) transactions that appear in a block

- (User -> Input) user that emitted bitcoin to an user
- (User -> User) shows the bitcoin flow through addresses
############

The Input dataset has been completed with the bitcoin amout: 
it was enough to find the output from which the input was created using the foreign key

The Transaction dataset has been completed calculating the fee for each transaction as follow:
fee = I(amount) - O(amount)

The User dataset has been created as follow:
for each pk that appear in (Input U Output) create a new User.
the user balance at the last block has been calculated as the sum of the User's incoming outputs 
minus the sum of the outcoming inputs:

B(u) = O(u) - I(u)

throughout the dataset were find the corrupted datas: 
- Negative values as output
- Outputs with too much bitcoins with respect to the input they come from
- Doublespended bitcoins (outputs used in more than one input)
- inputs emitted from addresses that never received the related amount

with the dataset thus created it is possible to perform more analyses 
than those suggested:

- We can consider the whole richness circulating in the blockchain at the last block
as the total sum emitted from the coinbase - total fees to see:
--- how many Bitcoins the system get back with respect to how many it emitted
--- the distibution of richness among the user, with the richness formalized as the amount of bitcoin owned by a user
--- Gini coefficient 

I would have liked to go deeper into the analysis, but I did not have enough time
"""


app = App()

while True:
    print(
        """
        Enter a command:

        - 't' -> Unpack the transaction and populate the DB with the nodes
        - 'o' -> Unpack the outputs, populate and create relationship with transactions
        - 'i' -> Unpack the inputs, populate and create relationship with transactions
        - 'ot' -> Create relationships IS_OUTPUT_OF (link the output to the transaction it is part of)
        - 'it' -> Create relationships IS_INPUT_OF (link the input to the transaction it is part of)
        - 'oi' -> Create relationships USED_AS_INPUT (link the previous output to a new input)
        - 'io' -> Create relationships USED_AS_OUTPUT (link the input to the outputs that are in the same transaction)
        - 'i_ids' -> Return a list of input ids
        - 'val' -> Update the values of the output nodes
        - 'check' -> Check the dataset correctness
        - 'UTXO' -> Return the list of UTXO outputs
        - 'user' -> Create user nodes given their pubkey
        - 'track' -> Create relationship between users and outputs (s)he appears in
        - 'track2' -> Create relationship between users and inputs (s)he appears in
        - 'balances' -> Compute all the balances
        - 'size' -> Compute the size and the distribution of the blocks
        - 'outcons' -> Find the inconsistent output (without an input)
        - 'amount' -> Calculate and plot the transacitons amount distribution
        - 'fees' -> Plot the fees distribution

        - 'q' -> Quit 
        """
        )

    command = str(input())
    
    if command == 'q':
        print('Bye!')
        break


    elif command == 't':
        transactions = Unpacker.unpack_transactions()
        app.create_blocks_of_transactions(transactions) #method to populate the bd with transactions
        
    elif command == 'o':
        outputs = Unpacker.unpack_outputs()
        app.create_output_nodes(outputs)

    elif command == 'i':
        inputs = Unpacker.unpack_inputs()
        app.create_input_nodes(inputs)

    elif command == 'val':
        outputs = Unpacker.unpack_outputs()
        app.set_value(outputs)

    elif command == 'fees':

        res = app.calculate_fees()
        invalid_transactions = []
        with open('huge.json', 'r') as h:
            invalid_transactions = json.load(h)['invalid_transactions']
        Plot.plot_fees(res, invalid_transactions)

    elif command == 'flow':

        app.exec_query("match (u1:User)-[]->(i:Input)-[]->(o:Output)-[]->(u2:User), (u1)-[f:FLOW]->(u2) set f.amount = 0", None)
        app.exec_query("match (u1:User)-[]->(i:Input)-[]->(o:Output)-[]->(u2:User), (u1)-[f:FLOW]->(u2) set f.amount = f.amount + o.value", None)

    elif command == 'amount':

        if exists('huge.json'):

            with open('huge.json', 'r') as h:
                dict = json.load(h)

            outputs = Unpacker.unpack_outputs()
            Blind_logic.transaction_amount(outputs, dict)
        
        else:
            print("You have to exec 'check' command beore!")

    elif command == 'check':

        inputs = Unpacker.unpack_inputs()
        outputs = Unpacker.unpack_outputs()
        transactions = Unpacker.unpack_transactions()


        Blind_logic.check(inputs, outputs, transactions)

    elif command == 'ot':
        query_rel = """
                    match
                        (o:Output),
                        (t:Transaction)
                    where o.trx_id = t.id
                    merge (o)-[r:IS_OUTPUT_OF]->(t)
                    """
        app.exec_query(query_rel, None)

    elif command == 'i_ids':
        inputs = Unpacker.unpack_inputs()
        ids = Blind_logic.find_input_ids(inputs)
        print(ids)

    elif command == 'UTXO':
        inputs = Unpacker.unpack_inputs()
        outputs = Unpacker.unpack_outputs()
        utxo = Blind_logic.find_input(inputs, outputs)
        app.exec_query("match (o:Output) set o.utxo = 0", None)
        app.exec_query("match (o:Output) where o.o_id in $param set o.utxo = 1", utxo)

    elif command == 'wealth':

        coinbase_emitted, transactions, users = app.wealth()
        invalid_transactions = []
        with open('huge.json', 'r') as h:
            invalid_transactions = json.load(h)['invalid_transactions']

        Blind_logic.compute_wealth_distr(coinbase_emitted, transactions, users, invalid_transactions)


    elif command == 'balances':

        pubkeys = Blind_logic.find_pubkeys('', '')
        for pk in pubkeys:  
            if pk != 0:
                app.exec_query("match (u:User {pk: $param}) set u.balance = 0", pk)
                app.exec_query(
                """
                match (u:User {pk: $param})
                match (u)-[s:SENT]->(i:Input) 
                set u.balance = u.balance - i.value
                """, pk)                

                app.exec_query(
                """
                match (u:User {pk: $param})
                match (o:Output)-[r:RECEIVED]->(u) 
                set u.balance = u.balance + o.value
                """, pk)  

    elif command == 'it':
        query_rel = """
                        match
                            (i:Input),
                            (t:Transaction)
                        where i.trx_id = t.id
                        merge (i)-[r:IS_INPUT_OF]->(t)
                        """
        app.exec_query(query_rel, None)

    elif command == 'oi':
        query_rel = """
                        match
                            (i:Input),
                            (o:Output)
                        where i.o_id = o.o_id
                        merge (o)-[r:USED_AS_INPUT]->(i)
                        """
        app.exec_query(query_rel, None)

    elif command == 'user':
        
        inputs = Unpacker.unpack_inputs()
        outputs = Unpacker.unpack_outputs()
        pubkeys = Blind_logic.find_pubkeys(inputs, outputs)
        for pk in pubkeys:
            app.exec_query("""merge (u:User {pk: $param, balance: 0})""", pk)

    elif command == 'size':
        transactions = Unpacker.unpack_transactions()
        sizes = Blind_logic.compute_blocks_size(transactions)

    elif command == 'track':

        outputs = Unpacker.unpack_outputs()
        o_ids = Blind_logic.build_list(outputs, 0)
        print('im here')
        try:
            session = app.create_connection()
            for o in o_ids:
                print('did 1')
                create_rel = """
                match (o:Output {o_id: $param})
                where o.o_id <> 0
                merge (u:User {pk: o.pub_key, balance: 0})
                merge (o)-[r:RECEIVED]->(u)
                """
                app.exec_query(create_rel, o)
        except:
            session.close()

        session.close()
    
    elif command == 'track2':

        inputs = Unpacker.unpack_inputs()
        i_ids = Blind_logic.build_list(inputs, 0)
        print('im here track2')
        try:
            session = app.create_connection()

            for i in i_ids:
                print('did it input')
                create_rel = """
                match (i:Input {i_id: $param})
                where i.o_id <> 0
                merge (u:User {pk: i.sig_id, balance: 0})
                merge (i)<-[r:SENT]-(u)
                """
                app.exec_query(create_rel, i)
        except:
            session.close()

        session.close()

    elif command == 'coinbase':
        
        if exists('huge.json'):
            with open('huge.json', 'r') as h:
                dict = json.loads(h)
            
            illegal_outputs = dict['invalid_output_pk'] + dict['output_without_value'] + dict['double_spended']
            inputs = Unpacker.unpack_inputs()
            outputs = Unpacker.unpack_outputs()
            Blind_logic.build_users(inputs, outputs, illegal_outputs)
        else:
            print("execute 'check' command before!")

    elif command == 'io':
        query_rel = """
                        match
                            (i:Input),
                            (o:Output)
                        where i.trx_id = o.trx_id
                        merge (i)-[r:USED_AS_OUTPUT]->(o)
                        """
        app.exec_query(query_rel, None)
