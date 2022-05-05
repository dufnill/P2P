import logging
from os.path import exists
from neo4j import GraphDatabase
from neo4j.exceptions import ServiceUnavailable
from Plot import Plot

"""
This class is used to perform action to the Noe4j DB
"""

class App:

    def __init__(self):
        return

    def create_connection(self):
        return GraphDatabase.driver(uri = "bolt://localhost:7687", auth = ("neo4j", "password")).session()

    #method to find the distribution of wealth
    def wealth(self):
        session = self.create_connection()

        try:

            query ="match (u:User{pk:0}) return u.balance as balance"
            res1 = session.run(query)
            coinbase_emitted = []
            for record in res1:
                coinbase_emitted.append(record.values())

            query = "match (t:Transaction) return t.id, t.fee, t.input_total, t.output_total as transaction"
            res2 = session.run(query)
            transactions = []
            for record in res2:
                transactions.append(record.values())

            query = "match (u:User) where u.pk > 0  return u.pk, u.balance as user"
            res3 = session.run(query)
            users = []
            for record in res3:
                users.append(record.values())
                
            session.close()

            return coinbase_emitted, transactions, users

        except Exception as ex:
            
            template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            message = template.format(type(ex).__name__, ex.args)
            print (message)

        print('DB correctly populated!')
        session.close()
        return

    #method to populate the bd with transactions
    def create_blocks_of_transactions(self, transactions):

        session = self.create_connection()

        try:

            for transaction in transactions:

                trx_id = transaction[0]
                block_num = transaction[1]
                query ="""
                        merge (b:Block { block_num: $block_num }) 
                        merge (t:Transaction { id: $trx_id }) 
                        merge (t)-[r:IS_IN_BLOCK]->(b)
                        """
                session.run(query, block_num = int(block_num), trx_id = int(trx_id))

        except Exception as ex:
            
            template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            message = template.format(type(ex).__name__, ex.args)
            print (message)

        print('DB correctly populated!')
        session.close()
        return

    #method to add the value of the output in the output nodes
    def set_value(self, outputs):

        session = self.create_connection()
        try:

            for output in outputs:

                o_id = output[0]
                value = output[3]
                query_merge ="""match (o:Output {o_id: $o_id}) set o.value = $value"""
                session.run(query_merge, o_id = int(o_id), value = int(value))
            
        except Exception as ex:
            
            template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            message = template.format(type(ex).__name__, ex.args)
            print (message)
            session.close()
            return

        print('Values correclty updated!')
        session.close()

    #method to populate the bd with outputs
    def create_output_nodes(self, outputs):

        session = self.create_connection()
        try:

            for output in outputs:

                o_id = output[0]
                trx_id = output[1]
                pub_key = output[2]
                value = output[3]
                query_merge ="""merge (o:Output { o_id: $o_id, trx_id: $trx_id, pub_key: $pub_key, value: $value })"""
                session.run(query_merge, o_id = int(o_id), trx_id = int(trx_id), pub_key = int(pub_key), value = int(value))
            
        except Exception as ex:
            
            template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            message = template.format(type(ex).__name__, ex.args)
            print (message)
            session.close()
            return

        print('DB correctly populated!')
        session.close()

        #create the relationship between outputs and transactions
        query_rel = """
                    match
                        (o:Output),
                        (t:Transaction)
                    where o.trx_id = t.id
                    merge (o)-[r:IS_OUTPUT_OF]->(t)
                    """
        res = self.exec_query(query_rel, None)
        return res

    #method to populate the bd with inputs
    def create_input_nodes(self, inputs):
    
        session = self.create_connection()
        try:

            for input in inputs:

                i_id = input[0]
                trx_id = input[1]
                sig_id = input[2]
                o_id = input[3]
                query_merge ="""merge (i:Input { i_id: $i_id, trx_id: $trx_id, sig_id: $sig_id, o_id: $o_id })"""
                session.run(query_merge, i_id = int(i_id), trx_id = int(trx_id), sig_id = int(sig_id), o_id = int(o_id))
            
        except Exception as ex:
            
            template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            message = template.format(type(ex).__name__, ex.args)
            print (message)
            session.close()
            return

        print('DB correctly populated!')
        session.close()

        #create the relationship between inputs and transactions
        query_rel = """
                        match
                            (i:Input),
                            (t:Transaction)
                        where i.trx_id = t.id
                        merge (i)-[r:IS_INPUT_OF]->(t)
                        """
        res = self.exec_query(query_rel,None)
        return res

    #method to calculate the fees applyed to each transaction
    def calculate_fees(self):

        if exists('fee_per_transasction.json'):
            with open('fee_per_transasction.json', 'r') as f:
                fees = json.loads(f)

        else:
            res = self.exec_query("MATCH (n:Transaction) RETURN n.id, n.fee, n.input_total, n.output_total as transaction", None)
            return res

    #method to execute a query
    def exec_query(self, query, param):
        try:

            session = self.create_connection()
            if param is None:
                res = session.run(query)
            else:
                res = session.run(query, param = int(param))

            ret = []

            for record in res:
                ret.append(record.values())

            session.close()
            return ret
            

        except Exception as ex:
            template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            message = template.format(type(ex).__name__, ex.args)
            print (message)
            session.close()
            return
