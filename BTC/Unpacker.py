import csv 

#this class unpack the csvs

class Unpacker():

    @staticmethod
    def unpack_inputs():
        inputs_array = []
        with open('inputs.csv') as i:
            for input in csv.reader(i, delimiter=','):
                new = []
                for i in input:
                    new.append(int(i))
                inputs_array.append(new)
        return inputs_array

    @staticmethod
    def unpack_transactions():
        transactions_array = []
        with open('transactions.csv') as t:
            for transaction in csv.reader(t, delimiter=','):
                new = []
                for t in transaction:
                    new.append(int(t))
                transactions_array.append(new)
        return transactions_array

    @staticmethod
    def unpack_outputs():
        outputs_array = []
        with open('outputs.csv') as o:
            for output in csv.reader(o, delimiter=','):
                new = []
                for o in output:
                    new.append(int(o))
                outputs_array.append(new)
        return outputs_array

