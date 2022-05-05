
from kademlia_manager import min_distance, lcp, right_rotate, reply, xor_dist
from time import sleep

rt = {}
k = 4
for i in range(0,2**(8)):
    rt[str((bin(i)[2:].zfill(8)))] = {
        '0': [],
        '1': [],
        '2': [],
        '3': [],
        '4': [],
        '5': [],
        '6': [],
        '7': []
    }

rt['11001010']['7'] = ['01001111', '00110011', '01010101', '00000010']
rt['11001010']['6'] = ['10110011', '10111000', '10001000']
rt['11001010']['5'] = ['11101010', '11101110', '11100011', '11110000']
rt['11001010']['4'] = ['11010011', '11010110']
rt['11001010']['3'] = ['11000111']

print('k-bucket 7 '+str(rt['11001010']['7']))
print('k-bucket 6 '+str(rt['11001010']['6']))
print('k-bucket 5 '+str(rt['11001010']['5']))
print('k-bucket 4 '+str(rt['11001010']['4']))
print('k-bucket 3 '+str(rt['11001010']['3']))
print('k-bucket 2 '+str(rt['11001010']['2']))
print('k-bucket 1 '+str(rt['11001010']['1']))
print('k-bucket 0 '+str(rt['11001010']['0']))

#POINT 1 #########################################################################################################
messages_from = ['01101001', '10111000', '11110001', '10101010', '11100011', '11111111']
node = '11001010'

for ID in messages_from:

    if ID == node:
        continue

    print("It's coming a message from "+ID+"...\n")
    
    #find the bucket where the ID should be
    bucket = str(min_distance(node, ID))

    
    print("I have to look in the k-bucket "+bucket+"\n")



    #The ID is already in the bucket
    if ID in rt[node][bucket]:

        print("The ID "+ID+" was alredy there!\n")
        rt[node][bucket].remove(ID) 
        rt[node][bucket].append(ID)

    #The ID isn't in the bucket
    else:

        print("The ID "+ID+" is not there!\n")


        #The bucket isn't full
        if len(rt[node][bucket]) < k:
            print("There is enough space in the bucket "+bucket+" for "+ID+", join!\n")
            rt[node][bucket].append(ID)

        #The bucket is full
        else:

            #The last recent contacted node replied
            if not reply(rt[node][bucket][0]):
                rt[node][bucket].pop(0)  
                rt[node][bucket].append(ID)

            #The last recent contacted node didn't reply
            else: 
                rt[node][bucket] = right_rotate(rt[node][bucket])
                print("I had to discard "+ID+", I'm sorry.\n")


    print('k-bucket 7 '+str(rt['11001010']['7']))
    print('k-bucket 6 '+str(rt['11001010']['6']))
    print('k-bucket 5 '+str(rt['11001010']['5']))
    print('k-bucket 4 '+str(rt['11001010']['4']))
    print('k-bucket 3 '+str(rt['11001010']['3']))
    print('k-bucket 2 '+str(rt['11001010']['2']))
    print('k-bucket 1 '+str(rt['11001010']['1']))
    print('k-bucket 0 '+str(rt['11001010']['0'])+'\n')

    print("\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n")

#############################################################################################################
# POINT 2 ###################################################################################################

not_reachable = '11101110'
bucket = str(min_distance(node, not_reachable))
rt[node][bucket].remove(not_reachable)
print("I would remove "+not_reachable+" from bucket "+str(bucket))
print('k-bucket 7 '+str(rt['11001010']['7']))
print('k-bucket 6 '+str(rt['11001010']['6']))
print('k-bucket 5 '+str(rt['11001010']['5']))
print('k-bucket 4 '+str(rt['11001010']['4']))
print('k-bucket 3 '+str(rt['11001010']['3']))
print('k-bucket 2 '+str(rt['11001010']['2']))
print('k-bucket 1 '+str(rt['11001010']['1']))
print('k-bucket 0 '+str(rt['11001010']['0'])+'\n')
print("\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n")

#############################################################################################################
# POINT 3 ###################################################################################################

look_for = '11010010'
min_dist = 2**(8)
neighbour = ''

for kb, list in rt[node].items():
    for ID in list:
        dist = xor_dist(look_for, ID)
        print(ID,dist)
        if dist < min_dist:
            min_dist = dist
            neighbour = ID
print("I would ask to "+str(neighbour)+", because it is at distance "+str(min_dist))