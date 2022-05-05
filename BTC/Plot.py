import matplotlib.pyplot as plt
import json
import numpy as np

#class used to plot some datas 

class Plot:

    @staticmethod
    def plot_wealth(wealth_distr):

        perctot50 = 0
        perctot60 = 0
        perctot70 = 0
        perctot80 = 0
        perctot90 = 0
        perctot100 = 0
        perctot = 0

        n50 = 0
        n60 = 0
        n70 = 0
        n80 = 0
        n90 = 0
        n100 = 0
        ntot = 0
        tozero = 0 
        upzero = 0

        for pk,bal in wealth_distr.items():

            if bal == 0:
                tozero += 1
                ntot += 1
            else:
                ntot += 1
                upzero += 1
                perctot += bal

                if perctot50 < 50:
                    perctot50 += bal
                    n50 += 1

                if perctot60 < 60:
                    perctot60 += bal
                    n60 += 1

                if perctot70 < 70:
                    n70 += 1
                    perctot70 += bal
                
                if perctot80 < 80:
                    n80 += 1
                    perctot80 += bal
                
                if perctot90 < 90:
                    n90 += 1
                    perctot90 += bal
                
                if perctot100 < 100:
                    n100 += 1
                    perctot100 += bal

        with open('report.txt', 'a+') as r:
            
            r.write('100% della ricchezza è detenuta dallo '+str(100*n100/ntot)+'% degli indirizzi, '+str(ntot)+' utenti\n')
            r.write('90% della ricchezza è detenuta dallo '+str(100*n90/ntot)+'% degli indirizzi, '+str(n90)+' utenti\n')
            r.write('80% della ricchezza è detenuta dallo '+str(100*n80/ntot)+'% degli indirizzi, '+str(n80)+' utenti\n')
            r.write('70% della ricchezza è detenuta dallo '+str(100*n70/ntot)+'% degli indirizzi, '+str(n70)+' utenti\n')
            r.write('60% della ricchezza è detenuta dallo '+str(100*n60/ntot)+'% degli indirizzi, '+str(n60)+' utenti\n')
            r.write('50% della ricchezza è detenuta dallo '+str(100*n50/ntot)+'% degli indirizzi, '+str(n50)+' utenti\n')
            r.write('Ho contato '+str(ntot)+' utenti\n')
            r.write('Ci sono '+str(tozero)+" indirizzi con bilancio a zero\n")
            r.write('Ci sono '+str(upzero)+' indirizzi con bilancio maggiore di zero\n')


    @staticmethod
    def gini(users):

        up = 0
        down = 0

        j = 1
        n = 0

        for pk,bal in users.items():
            if bal >= 0:
                n += 1
        for pk,bal in users.items():
            
            if bal >= 0:
                up += (n + 1 - j)*bal
                down += bal
                j += 1

        gini = (1/n) * (n+1-2*(up/down))

        with open('report.txt', 'a+') as r:
            r.write('Coefficiente di Gini calcolato: '+str(gini)+'\n\n\n\n')
        

    @staticmethod
    def plot_fees(list, invalid_transactions):

        j = 1
        sum = 0
        count = 0
        step = int(len(list)/24)
        x = []
        y = []

        for [k,f,i,o] in list:

            if f >= 0 and k not in invalid_transactions:

                count = count + 1
                sum = sum + (100-int(o/i*100))

            if count == step:
                y.append(sum/count)
                x.append(j)
                j+=1
                count = 0
                sum = 0

        print(x,y)
        plt.grid()
        plt.plot(x, y, '-o')
        plt.ylabel('%')
        plt.xlabel('Months')
        plt.title('Fees evolution')
        plt.savefig('fees_distribution.png')
        plt.clf()

    @staticmethod
    def plot_amount(dict):

        size = 0
        for k,v in dict.items():
            size += 1
        step = int(size/24)
        
        count = 0
        sum = 0
        i = 0
        x = []
        y = []
        
        for k,v in dict.items():
            if count == step:
                y.append((sum/count)/1000000000)
                x.append(i)
                sum = 0
                count = 0
                i += 1
            else:
                count += 1
                sum += v


        plt.grid()
        plt.ylabel("Billions of BTC")
        plt.xlabel("Months")
        plt.plot(x, y, '-o')
        plt.savefig('amount_distribution.png')
        plt.clf()

    @staticmethod
    def plot_blocks(size, distr):

        dict = {}
        n_blocks = len(size)
        n_rounds = len(distr)

        x1 = list(range(n_blocks))
        x2 = list(range(n_rounds))
        
        plt.grid()
        plt.scatter(x1, size, s=1)
        plt.xlabel('Blocks')
        plt.ylabel('Transactions per block')
        plt.title('Transactions denisty per block')
        plt.savefig('block_size_distribution.png')
        plt.clf()
        plt.title('Distribution')
        plt.grid()
        plt.xlabel('Months')
        plt.ylabel('Avg transactions per block')
        plt.title('Transactions average density')
        plt.plot(x2, distr, '-o')
        plt.savefig('block_size_distribution_step_1_month.png')
        plt.clf()
