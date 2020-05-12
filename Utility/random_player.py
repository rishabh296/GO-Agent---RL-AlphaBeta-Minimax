
# coding: utf-8

# In[244]:


import pandas as pd
import numpy as np
import random
from sys import maxsize
import time

prefix = "C:\\Users\\abc\\Desktop\\USC\\Spring 20\\CSCI 561 - AI\\HW\\HW2\\Code\\asnlib\\public\\myplayer_play\\"


file_r = open(prefix+"input.txt", "r")
roundNo = 1
try:
    file_c_r = open(prefix+"count.txt", "r")
    roundNo = int(file_c_r.read().split('\n')[0])
    file_c_w = open(prefix+"count.txt", "w")
except:
    file_c_w = open(prefix+"count.txt", "w")
    pass
file_w = open(prefix+"output.txt", "w")
# file_a = open(prefix+r"\Qs.txt", "a")

def createIntMatrix(string):
    state=[]
    row=[]
    count=0
    for char in string:
        try:
            i = int(char)
            row.append(i)
            count+=1
            if count==5:
                state.append(row)
                row,count = [],0
        except:
            continue
    return state

def countZeros(state):
    zeros = 0
    for row in state:
        zeros+=row.count(0)
    return zeros

inp = file_r.read().split('\n')
iam = int(inp[0])
opponent = 1 if iam==2 else 2
N=5
v = None
komi = N/2
prev = []
new = []
global depth_cutoff

for i in range(1,N+1):
    row = []
    for j in inp[i]:
        row.append(int(j))
    prev.append(row)

for i in range(N+1,(2*N)+1):
    row = []
    for j in inp[i]:
        row.append(int(j))
    new.append(row)

prev_vacant = countZeros(prev)
new_vacant = countZeros(new)

if prev_vacant==25:
    roundNo = 2
if new_vacant==25:
    roundNo = 1

depth_cutoff = 5 if iam==2 else 4
if iam==1:
    if roundNo<=13:
        depth_cutoff=4
    else:
        depth_cutoff=6

depth_cutoff=min(depth_cutoff,24-roundNo)

def checkKO(prev,new, v):
    try:
        KO = []
        for row in range(0,len(new)):
            for val in range(0,len(new[row])):
                if new[row][val]!=prev[row][val] and prev[row][val]==v:
                    KO.append((row,val))
                if len(KO)>1:
                    return None
        temp = copyState(new)
        i,j = KO[-1]
        temp[i][j] = v
        opp = 1 if v==2 else 2
        if countZeros(checkLiberty(temp, opp, KO[-1]))>countZeros(new):
            return None
        return KO[-1]
    except:
        return None

def checkLiberty(state, whose, index):
    #liberty elimination
    if index=='PASS':
        return state
    ok = set({})
    row,val = index
    x = [1,-1,0,0]
    y = [0,0,-1,1]
    indices=[]
    
    #Creating indices we need to check for based on the NEW MOVE
    if state[row][val]==whose:
        indices.append((row,val))
    else:
        for i in range(len(x)):
            r = row+x[i]
            v = val+y[i]
            if (r<0) or (v<0) or r>=len(state) or v>=len(state[0]):
                continue
            else:
                indices.append((r,v))
    
    #BFS to Check liberties and eliminating captured pieces
    for index in indices:
        a,b = index
        curr = state[a][b]
        if curr==whose and (a,b) not in ok:
            liberty = [(a,b)]
            seen = set({})
            flag = True
            while len(liberty)!=0:
                rt,vt = liberty.pop(0)
                seen.add((rt,vt))
                for i in range(0,len(x)):
                    r = rt+x[i]
                    v = vt+y[i]
                    if (r<0) or (v<0) or r>=len(state) or v>=len(state[0]):
                        continue
                    if state[r][v]==0 or (r,v) in ok:
                        flag = False
                        break
                    elif state[r][v]==whose and ((r,v) not in seen) and ((r,v) not in liberty):
                        liberty.append((r,v))
                if not flag:
                    break
            if flag:
                for r,v in seen:
                    state[r][v] = 0
            else:
                ok.update(seen)
    return state

def evaluate(state):
    white = komi
    black = 0
    
    for row in state:
        white+=row.count(2)
        black+=row.count(1)
    
    if iam==1:
        return (black-white)
    else:
        return (white-black)

def terminal(state, depth):
    if depth>depth_cutoff:
        return True

def action(state, player,rival):
    vacancies = []
    for row in range(0,len(state)):
        for val in range(0,len(state[row])):
            if state[row][val]==0:
                if (row,val)==KO:
                    continue
                flag=False
                temp = copyState(state)
                temp[row][val]=player
                temp2 = checkLiberty(copyState(temp),rival,(row,val))
                temp3 = checkLiberty(copyState(temp),player,(row,val))
                
                opp1,opp2,me1,me2=0,0,0,0
                for u in range(len(temp)):
                    opp1+=temp[u].count(rival)
                    me1+=temp[u].count(player)
                    opp2+=temp2[u].count(rival)
                    me2+=temp3[u].count(player)
                if opp2<opp1 or me2==me1:
                    vacancies.append((row,val))
    return vacancies+['PASS']

def result(state,a, value):
    if a=='PASS':
        return state
    row,val = a
    state[row][val] = value
    return state

def copyState(state):
    newState = []
    for row in state:
        newState.append(row[:])
    return newState

dict_v = dict({})
def max_alphabeta(state, alpha, beta, depth, score, ko=None):
    vacancies = action(state,iam,opponent)
    if terminal(state,depth) or len(vacancies)==0 or vacancies==[ko]:
        return evaluate(state)
    
    mini = -float('inf')
    for a in vacancies:
        if a==ko:
            continue
        newState = checkLiberty(result(copyState(state),a,iam),opponent,a)
        newScore = evaluate(newState)
        if ((newScore<score) or (newScore==score and depth>=2)) and a!='PASS':
            continue
        value = min_alphabeta(newState, alpha, beta,depth+1, newScore, checkKO(state, newState, iam))
        mini = max(mini,value)
        alpha = max(mini,alpha)
        if depth==startDepth():
            try:
                dict_v[value].add(a)
            except:
                dict_v[value] = {a}
        if alpha>=beta:
            break
    if mini==-float('inf'):
        if iam==1:
            return evaluate(state)
        return evaluate(state)+1
    return mini

def min_alphabeta(state, alpha, beta,depth, score, ko=None):
    vacancies = action(state,opponent,iam)
    if terminal(state,depth) or len(vacancies)==0 or vacancies==[ko]:
        return evaluate(state)
    maxy = float('inf')
    for a in vacancies:
        if a==ko:
            continue
        newState=checkLiberty(result(copyState(state),a, opponent),iam,a)
        maxy = min(maxy,max_alphabeta(newState, alpha, beta,depth+1, score, checkKO(state, newState, opponent)))
        beta = min(maxy,beta)
        if beta<=alpha:
            break
    return maxy

def blackLiberty(filtered,new,a,opponent):
    #black logic - Attack Enemy Liberty
    black = []
    mini=float('inf')
    for a in filtered:
        count1,count2 = enemyLiberty(copyState(new),a, opponent)
        if (count2<mini or len(black)==0) and count1>0:
            mini=count2
            black = [a]
        elif count2==mini and count1>0:
            black.append(a)
    print('Agressive Black Enemy Liberty - ',mini, black)
    if len(black)==0:
        return filtered
    return black

def teammate(filtered, state):
    #checking team player arround me
    x,y = [1,-1,0,0,1,1,-1,-1],[0,0,1,-1,-1,1,1,-1]
    temperary = []
    for a in filtered:
        if a=='PASS':
            continue
        for i in range(0,len(x)):
            r = a[0]+x[i]
            v = a[1]+y[i]
            if (r<0) or (v<0) or r>=len(new) or v>=len(new[0]):
                continue
            if new[r][v]==iam:
                temperary.append(a)
                break
    if len(temperary)>0:
        filtered=temperary
    print('Checking if Teammate Nearby - ',filtered)
    return filtered

def greedy(actions):
    greedy = []
    maxy = -float('inf')
    for a in actions:
        newState = checkLiberty(result(copyState(new),a,iam),opponent,a)
        score = evaluate(newState)
        if score>maxy:
            maxy=score
            greedy = [a]
        elif score==maxy:
            greedy.append(a)
    print('Greedy - ',actions, 'Ans - ',maxy,greedy)
    return greedy

def aggressive(actions):
    global iam
    global opponent
    global v
    maxy2 = float('inf')
    for a in actions:
        state = checkLiberty(result(copyState(new),a,iam),opponent,a)
        iam=opponent
        opponent=1 if iam==2 else 2
        value = max_alphabeta(state,float('-inf'),float('inf'), startDepth(), evaluate(state))
        iam=opponent
        opponent=1 if iam==2 else 2
        if value<maxy2:
            maxy2=value
            filtered=[a]
        elif value==maxy2:
                filtered.append(a)
    print('Agressive - ',actions,' After best enemy move - ',maxy2, filtered )
    if len(filtered)==1:
        return filtered
    elif len(filtered)==0:
        filtered=actions
    
    print('Global v = ',v)
    #if iam==1 or v<=0:
    filtered = teammate(filtered,copyState(new))
    #if v<=0:
    filtered = blackLiberty(filtered,copyState(new),a,opponent)
    
    liberty = []
    maxy=0
    for a in filtered:
        count = countLiberty(copyState(new),a, iam)
        if count>maxy:
            maxy=count
            liberty = [a]
        elif count==maxy:
            liberty.append(a)
    print('Agressive Liberty - ',maxy, liberty )
    if len(liberty)==1:
        return liberty
    elif len(liberty)==0:
        liberty=filtered

    #if iam==2 and v>0:
    #    liberty = teammate(liberty,copyState(new))
    
    #Picking Move with Max available liberty
    x,y = [1,-1,0,0],[0,0,1,-1]
    agressive = []
    maxy=0
    for a in liberty:
        if a=='PASS':
            continue
        state = checkLiberty(result(copyState(new),a,iam),opponent,a)
        opps = 0
        for i in range(0,len(x)):
            r = a[0]+x[i]
            v = a[1]+y[i]
            if (r<0) or (v<0) or r>=len(state) or v>=len(state[0]):
                continue
            opps+=(state[r][v]==opponent)
        if opps>maxy:
            maxy=opps
            agressive = [a]
        elif opps==maxy:
            agressive.append(a)
    print('Agressive Ans2 - ',maxy,agressive)
    return agressive

def enemyLiberty(state,index, val):
    #liberty elimination
    x = [1,-1,0,0]
    y = [0,0,-1,1]
    
    #BFS to Check liberties and eliminating captured pieces
    a,b = index
    state[a][b]=1 if val==2 else 1
    curr = state[a][b]
    liberty = []
    for i in range(len(x)):
        r = a+x[i]
        v = b+y[i]
        if (r<0) or (v<0) or r>=len(state) or v>=len(state[0]):
            continue
        elif state[r][v]==val:
            liberty.append((r,v))
    
    seen = set({})
    seen2 = set({})
    count=0
    while len(liberty)!=0:
        rt,vt = liberty.pop(0)
        seen.add((rt,vt))
        for i in range(0,len(x)):
            r = rt+x[i]
            v = vt+y[i]
            if (r<0) or (v<0) or r>=len(state) or v>=len(state[0]):
                continue
            if state[r][v]==val and ((r,v) not in seen) and ((r,v) not in liberty):
                liberty.append((r,v))
            if state[r][v]==0 and ((r,v) not in seen2) :
                seen2.add((r,v))
                count+=1
    return len(seen), count

def countLiberty(state,index, val):
    #liberty elimination
    x = [1,-1,0,0]
    y = [0,0,-1,1]
    count=0
    
    #BFS to Check liberties and eliminating captured pieces
    a,b = index
    state[a][b]=val
    curr = state[a][b]
    liberty = [(a,b)]
    seen = set({})
    while len(liberty)!=0:
        rt,vt = liberty.pop(0)
        seen.add((rt,vt))
        for i in range(0,len(x)):
            r = rt+x[i]
            v = vt+y[i]
            if (r<0) or (v<0) or r>=len(state) or v>=len(state[0]):
                continue
            if state[r][v]==0 and ((r,v) not in seen) :
                seen.add((r,v))
                count+=1
            elif state[r][v]==curr and ((r,v) not in seen) and ((r,v) not in liberty):
                liberty.append((r,v))
    return count

def get_Best_Play(v,t):
    global iam
    global opponent
    if len(dict_v)==0:
            return 'PASS'
    if v not in dict_v.keys():
        v = max(dict_v.keys())
        return get_Best_Play(v)
    
    actions = action(copyState(new),iam,opponent)
    rand = list(dict_v[v])
    print('Rand, v and dict is - ',rand, v,dict_v)
    if (time.time()-t)<6.0:
        if len(rand)>1:
            rand = greedy(rand)
        if len(rand)>1:
            rand = aggressive(rand)
    rand = random.choice(rand)
    if rand not in actions:
        dict_v[v].remove(rand)
        rand = get_Best_Play(v)
    return rand

def startDepth():
    if iam==1:
        if depth_cutoff%2==0:
            return 1
        return 0
    else:
        if depth_cutoff%2==0:
            return 0
        return 1

KO = checkKO(prev,new, iam)
t = time.time()
text=''
rand = []
if new_vacant==25:
    text = '2,2'
elif prev_vacant==25 and new[2][2]==0:
    text = '2,2'
elif len(action(copyState(new),iam,opponent))==0:
    text = 'PASS'
else:
    t1= time.time()
    v = max_alphabeta(copyState(new),float('-inf'),float('inf'), startDepth(), evaluate(new))
    print(time.time()-t1)
    temp = depth_cutoff
    depth_cutoff=1
    t2 = time.time()
    rand = get_Best_Play(v,t)
    print('Best Play Time - ',time.time()-t2)
    depth_cutoff=temp
    if rand =='PASS':
        text=rand
    else:
        text = str(rand[0])+','+str(rand[1])
tm = time.time()-t
print('Time Taken - ',tm)

try:
    file_w.write(text)
    file_c_w.write(str(roundNo+2))
    file_w.close()
    file_r.close()
    file_c_r.close()
    file_c_w.close()
except:
    print('Some issue while writing and closing files')
