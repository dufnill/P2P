from random import seed
from random import randint

def xor_dist(id1,id2):
    if len(id1) != len(id2):
        return('error')
    else:
        dist = ''
        for i in range(0, len(id1)):
            if id1[i] == id2[i]:
                dist = dist + '0'
            else:
                dist = dist + '1'
        return int(dist, 2)

def lcp(id1, id2):
    
    if len(id1) != len(id2):
        return('error')
    matches = 0
    for i in range(0, len(id1)):
        if id1[i] == id2[i]:
            matches += 1
        else:
            break
    return matches

def min_distance(id1, id2):
    
    if len(id1) != len(id2):
        return('error')
    L = len(id1)
    p = lcp(id1,id2)
    i = L - p
    return i - 1

def right_rotate(list):
    return list[1:] + list[:1]

def reply(id):

    reply = randint(0, 1)
    if reply == 1:
        print(id+" replied back!")
    else:
        print(id+" didn't reply back!")
    return reply


