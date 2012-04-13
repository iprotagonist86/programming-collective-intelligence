#-*- coding: UTF-8 -*-

import random
import math
import optimization

# 각각 두 개의 방을 가진 기숙사들
dorms = ['Zeus', 'Athena', 'Hercules', 'Bacchus', 'Pluto']

# 첫 번째와 두 번째 선택을 한 사람 목록
prefs = [('Toby', ('Bacchus', 'Hercules')),
         ('Steve', ('Zeus', 'Pluto')),
         ('Andrea', ('Athena', 'Zeus')),
         ('Sarah', ('Zeus', 'Pluto')),
         ('Dave', ('Athena', 'Bacchus')),
         ('Jeff', ('Hercules', 'Pluto')),
         ('Fred', ('Pluto', 'Athena')),
         ('Suzie', ('Bacchus', 'Hercules')),
         ('Laura', ('Bacchus', 'Hercules')),
         ('Neil', ('Hercules', 'Athena'))]

# [(0,9), (0,8), (0,7), ... , (0,0)]
domain = [(0, (len(dorms)*2)-i-1) for i in range(0, len(dorms)*2)]


def printsolution(vec):
    slots = []
    # 각 기숙사마다 두 개의 방을 만듦
    for i in range(len(dorms)): slots += [i,i]
    
    # 루프를 돌면서 학생들을 배정함
    for i in range(len(vec)):
        x = int(vec[i])
        
        # 남은 것 중에 방을 선택함
        dorm = dorms[slots[x]]
        # 학생과 배정받은 기숙사를 출력함
        print prefs[i][0], dorm
        # 배정된 방을 제거함
        del slots[x]

#printsolution([0,0,0,0,0,0,0,0,0,0])
vec = [random.randint(domain[i][0], domain[i][1])
               for i in range(len(domain))]
#print vec
#printsolution(vec)

def dormcost(vec):
    cost = 0
    # 방 목록을 생성함
    slots = []
    for i in range(len(dorms)): slots += [i,i]
    
    # 각 학생별로 루프를 돔
    for i in range(len(vec)):
        x = int(vec[i])
        dorm = dorms[slots[x]]
        pref = prefs[i][1]
        # 첫 번째 선택 비용은 0, 두 번째 선택 비용은 1, 목록에 없으면 비용은 3
        if pref[0] == dorm: cost += 0
        elif pref[1] == dorm: cost += 1
        else: cost += 3
        
        # 배정한 방을 제거함
        del slots[x]
        
    return cost


s = optimization.randomoptimize(domain, dormcost)
print dormcost(s), s
#printsolution(s)
s = optimization.geneticoptimize(domain, dormcost)
print dormcost(s), s
#printsolution(s)