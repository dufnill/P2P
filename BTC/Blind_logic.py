import time
import json

from operator import itemgetter
from os.path import exists
from Plot import Plot
from collections import Counter

"""
Used to perform analysis using the csv files.
This design choise has been taken to perform the desired anlysis in a reasonable time
using the neo4j dataset would have taken too much time because of complex queries
"""

class Blind_logic:

    
    @staticmethod
    #method that calculate the amount spent in each transaction
    def transaction_amount(outputs, dict):

        invalid_ids = [k[0] for k in dict['invalid_output_pk']] + [k[0] for k in dict['output_without_value']] + [k[0] for k in dict['double_spended']]

        transactions = {}
        for o in outputs:

            if int(o[0]) in invalid_ids:
                continue
            else:
                if o[0] in transactions:
                    transactions[o[0]] = transactions[o] + int(o[3])
                else:
                    transactions[o[0]] = int(o[3])

        with open('amount_distr.json', 'w+') as f:
            f.write(json.dumps(transactions))
        
        Plot.plot_amount(transactions)


    @staticmethod
    #method to compute walt distribution
    def compute_wealth_distr(coinbase_emitted, transactions, users, invalid_transactions):
        
        total = -coinbase_emitted[0][0]
        fees = 0
        
        for [id, f, it, ot] in transactions:
            if id not in invalid_transactions:
                fees += f
        percfee = 100*(fees/total)

        with open('total_amount.json', 'w+') as t:
            t.write(json.dumps({'tot':total, 'fees':fees, 'perc_fees':percfee}))

        wealth_distr = {}
        users_dict = {}
        tot_users = 0

        for [pk, bal] in users:
            users_dict[pk] = bal
            if bal == 0:
                tot_users += 1
                wealth_distr[pk] = 0
            if bal > 0:
                tot_users += 1
                wealth_distr[pk] = 100*(bal/total)

        #ordering the user balances
        sorted_keys = sorted(users_dict, key=users_dict.get, reverse = False)
        sorted_dict = {}
        for w in sorted_keys:
            sorted_dict[w] = users_dict[w]
        with open('users_wealth.json', 'w+') as u:
            u.write(json.dumps(sorted_dict))

        #oredring the wealth distribution
        sorted_keys = sorted(wealth_distr, key=wealth_distr.get, reverse = True)
        sorted_dict = {}
        for w in sorted_keys:
            sorted_dict[w] = wealth_distr[w]
        with open('wealth_distr.json', 'w+') as w:
            w.write(json.dumps(sorted_dict))

        dict = {}
        with open('users_wealth.json', 'r') as u:
            dict = json.load(u)
        Plot.gini(dict)
        dict = {}
        with open('wealth_distr.json', 'r') as w:
            dict = json.load(w)
        Plot.plot_wealth(dict)

    @staticmethod
    #method that check for corrupted datas
    def check(inputs, outputs, transactions):

        #extract input parameters
        input_ids = Blind_logic.build_list(inputs, 0)
        input_tx = Blind_logic.build_list(inputs, 1)
        input_pk = Blind_logic.build_list(inputs, 2)
        input_oid = Blind_logic.build_list(inputs, 3)

        #extract output parameters
        output_ids = Blind_logic.build_list(outputs, 0)
        output_tx = Blind_logic.build_list(outputs, 1)
        output_pk = Blind_logic.build_list(outputs, 2)
        output_val = Blind_logic.build_list(outputs, 3)

        #extract output parameters
        transaction_ids = Blind_logic.build_list(transactions, 0)
        transaction_block = Blind_logic.build_list(transactions, 1)

        dict = {
            'invalid_input_ids': [], 
            'invalid_input_tx': [], 
            'invalid_input_pk': [],
            'invalid_input_oid' : [],
            'inputs_by_coinbase': [],
            'inputs_without_output' : [],
            'inputs_without_tx' : [],
            'inputs_duplicated' : [],
            'inputs_strange': [],
            'outputs_duplicated' : [],
            'output_strange': [],
            'double_spended' : [],
            'invalid_outputs_ids': [],
            'invalid_output_tx': [],
            'invalid_output_pk': [],
            'output_without_value': [],
            'outputs_without_inputs': [],
            'transaciton_strange': [],
            'invalid_transactions': [],


            }

        #check on the inputs
        inputs_without_output = list(set(input_oid) - set(output_ids))
        inputs_without_tx = list(set(input_tx) - set(transaction_ids))
        inputs_duplicated = [k for k,v in Counter(input_ids).items() if v > 1]
        double_spended = [k for k,v in Counter(input_oid).items() if v > 1 and k != -1]
       
        for i in inputs:
    
            if len(i) != 4:
                dict['inputs_strange'].append(i)
            else:
                #basic checks on the properties
                if i[0] < 0 or not isinstance(i[0], int):
                    dict['invalid_input_ids'].append(i)
                    
                if i[0] in inputs_duplicated:
                    dict['inputs_duplicated'].append(i)
                    
                if i[1] < 0 or not isinstance(i[1], int):
                    dict['invalid_input_tx'].append(i)
                    
                if i[2] < -1 or not isinstance(i[2], int):
                    dict['invalid_input_pk'].append(i)
                    
                if i[2] in inputs_without_tx:
                    dict['inputs_without_tx'].append(i)
                    
                if i[3] == -1:
                    dict['inputs_by_coinbase'].append(i)

                if i[3] < -1 or not isinstance(i[3], int):
                    dict['invalid_input_oid'].append(i)

                if i[3] in double_spended:
                    dict['double_spended'].append(i)
                    
                if i[3] != -1 and i[3] in inputs_without_output:
                    dict['inputs_without_output'].append(i)

        #check on the outputs
        output_without_inputs = list(set(output_tx) - set(input_tx))     
        outputs_duplicated = [k for k,v in Counter(output_ids).items() if v>1] 

        for o in outputs:
    
            if len(o) != 4:
                dict['output_strange'].append(o)
            else:
                #basic checks on the properties
                if o[0] < 0 or not isinstance(o[0], int):
                    dict['invalid_outputs_ids'].append(o)
                    
                elif o[0] in outputs_duplicated:
                    dict['outputs_duplicated'].append(o)
                    
                if o[1] < 0 or not isinstance(o[1], int):
                    dict['invalid_output_tx'].append(o)
                    
                if o[1] in output_without_inputs:
                    dict['output_without_inputs'].append(o)
                    
                if o[2] < -1 or not isinstance(o[2],int):
                    dict['invalid_output_pk'].append(o)
                    
                if o[3] <= 0:
                    dict['output_without_value'].append(o)
                    

        transactions_without_inputs = list(set(transaction_ids) - set(input_tx))
        transactions_without_outputs = list(set(transaction_ids) - set(output_tx))

        for t in transactions:
            if len(t) != 2:
                dict['transaciton_strange'].append(t)
            else:
                #basic checks on the properties
                if t[0] < 0 or not isinstance(t[0], int) or t[1] < 0 or not isinstance(t[1], int):
                    dict['invalid_transaction'].append(t)
                if t in transactions_without_inputs or t in transactions_without_outputs:
                    dict['corrupted_transaction'].append(t)

        invalid_transactions = []
        for k,v in dict.items():
            if k != 'inputs_by_coinbase':
                for el in v:
                    invalid_transactions.append(el[1])

        dict['invalid_transactions'] = invalid_transactions

        with open('huge.json', 'a+') as h:
            h.write(json.dumps(dict))

    @staticmethod
    #method to build a list from a list of lists
    def build_list(list, item):
        new_list = []
        for el in list:
            new_list.append(int(el[item]))
        return new_list

    @staticmethod
    #method to build an ordered set from a list of lists
    def build_list_without_repetitions(list, item):
        new_list = []
        for el in list:
            if int(el[item]) not in new_list:
                new_list.append(int(el[item]))

        return sorted(new_list)

    @staticmethod
    #method to find UTXO outputs
    def find_inputs(inputs, outputs):
        
        if exists('output_foreing_to_input_id.json') and exists('output_id.json'):
            
            with open('output_foreing_to_input_id.json', 'r') as of:
                input_ids = json.load(of)['o']

            with open('output_id.json', 'r') as i:
                output_ids = json.load(i)['o']

        else:

            input_ids = Blind_logic.build_list(inputs, 3)
            output_ids = Blind_logic.build_list_without_repetitions(outputs, 0)

            with open('output_foreing_to_input_id.txt', 'a+') as of:
                dict = {}
                dict['o'] = input_ids
                of.write(json.dumps(dict))

            with open('output_id.txt', 'a+') as i:
                dict = {}
                dict['o'] = output_ids
                i.write(json.dumps(dict))


        #i = 0
        utxo = {}
        utxo['utxo_outputs'] = sorted(list(set(output_ids) - set(input_ids)))

        with open('utxo_outputs.json', 'w+') as u:
            u.write(json.dumps(utxo))
        return utxo['utxo_outputs']

    @staticmethod
    #method to find inputs ids 
    def find_input_ids(inputs):

        if exists('input_ids.json'):
            with open('input_ids.json', 'r') as i:
                input_ids = json.load(i)['i']
        else:

            input_ids = Blind_logic.build_list_without_repetitions(inputs, 0)
            ids = {}
            ids['i'] = input_ids
            with open('input_ids.json', 'a+') as i:
                i.write(json.dumps(ids))
        return ids

    @staticmethod
    #method to extract public keys from inputs and outputs
    def find_pubkeys(inputs, outputs):

        if exists('pubkeys.json'):
            
            with open('pubkeys.json', 'r') as p:
                pubkeys = json.load(p)['pk']
            
        else:

            input_pks = Blind_logic.build_list_without_repetitions(inputs, 2)
            output_pks = Blind_logic.build_list_without_repetitions(outputs, 2)
            pubkeys = list(set(input_pks).union(set(output_pks)))
            pk = {}
            pk['pk'] = pubkeys
            with open('pubkeys.json', 'a+') as f:
                f.write(json.dumps(pk))
            
        return pubkeys

    @staticmethod
    #method to calculate the block size as the numbers of transactions that appear in
    def compute_blocks_size(transactions):
        
        size_list = []
        block_id = transactions[0][1]
        n_tran = 1

        for i in range(1, len(transactions)):

            if transactions[i][1] != block_id:
                size_list.append(n_tran)
                block_id = transactions[i][1]
                print(n_tran)
                n_tran = 1

            else:
                n_tran += 1

        dict = {}
        dict['sizes'] = size_list
        n_blocks = len(size_list)
        months = 24
        round = int(n_blocks/months)
        avg_size = []
        i = 0
        picked_blocks = 0
        picked_tr = 0

        while i < n_blocks:
            if picked_blocks == round or i == n_blocks - 1:
                avg_size.append(picked_tr / picked_blocks)
                picked_tr = 0
                picked_blocks = 0
            else:
                picked_tr += size_list[i]
                picked_blocks += 1
            i += 1

        dict['distr'] = avg_size

        with open('blocks_size.json', 'a+') as b:
            b.write(json.dumps(dict))

        Plot.plot_blocks(dict['sizes'], dict['distr'])
        