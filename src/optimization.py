#-*- coding: UTF-8 -*-

import time
import random
import math

people = [('Seymour', 'BOS'),
          ('Franny', 'DAL'),
          ('Zooey', 'CAK'),
          ('Walt', 'MIA'),
          ('Buddy', 'ORD'),
          ('Les', 'OMA')]

# 뉴욕 라구아디아 공항
destination = 'LGA'

flights = {}
for line in file('../data/schedule.txt'):
    origin, dest, depart, arrive, price = line.strip().split(',')
    flights.setdefault((origin, dest), [])
    
    # 비행편 리스트에 나머지를 넣음
    flights[(origin, dest)].append((depart, arrive, int(price)))


def getminutes(t):
    x = time.strptime(t, '%H:%M')
    return x[3]*60+x[4]
#print getminutes('23:10')


def printschedule(r):
    for d in range(len(r)/2):
        name = people[d][0]
        origin = people[d][1]
        out = flights[(origin, destination)][r[2*d]]
        ret = flights[(destination, origin)][r[2*d+1]]
        print '%10s%10s %5s-%5s $%3s %5s-%5s $%3s' % (name, origin,
                                                      out[0], out[1], out[2],
                                                      ret[0], ret[1], ret[2])

#s = [1,4,3,2,7,3,6,3,2,4,5,3]
#printschedule(s)


def schedulecost(sol):
    totalprice = 0
    latestarrival = 0
    earliestdep = 24*60
    
    for d in range(len(sol)/2):
        # 출발, 도착 비행편을 얻음
        origin = people[d][1]
        outbound = flights[(origin, destination)][int(sol[2*d])]
        returnf = flights[(destination, origin)][int(sol[2*d+1])]
        
        # 전체 가격은 모든 출발, 도착 비행편의 가격임
        totalprice += outbound[2]
        totalprice += returnf[2]
        
        # 가장 늦은 도착 시간과 가장 이른 출발 시간을 추적함
        if latestarrival < getminutes(outbound[1]): latestarrival = getminutes(outbound[1])
        if earliestdep > getminutes(returnf[0]): earliestdep = getminutes(returnf[0])
        
    # 모든 사람들은 가장 늦게 도착하는 사람을 공항에서 기다려야 함
    # 또 이들은 도착하는 동시에 출발 비행편을 기다려야 함
    totalwait = 0
    for d in range(len(sol) / 2):
        origin = people[d][1]
        outbound = flights[(origin, destination)][int(sol[2*d])]
        returnf = flights[(destination, origin)][int(sol[2*d+1])]
        totalwait += latestarrival - getminutes(outbound[1])
        totalwait += getminutes(returnf[0]) - earliestdep
        
    # 이 해답에 추가 자동차 렌탈일이 있는지 점검함. 있다면 50$가 부가됨
    if latestarrival > earliestdep: totalprice += 50
    
    return totalprice + totalwait

#print schedulecost(s)


def randomoptimize(domain, costf):
    best = 99999999
    bestr = None
    for i in range(1000):
        # 무작위 해답을 생성함
        r = [random.randint(domain[i][0], domain[i][1])
             for i in range(len(domain))]
        
        # 비용을 구함
        cost = costf(r)
        
        # 이제까지의 최적 값과 비교함
        if cost < best:
            best = cost
            bestr = r
    return bestr

domain = [(0,8)] * (len(people)*2)
#print domain
#s = randomoptimize(domain, schedulecost)
#print s
#print schedulecost(s)
#printschedule(s)


def hillclimb(domain, costf):
    # 무작위 해답을 생성함
    sol = [random.randint(domain[i][0], domain[i][1])
           for i in range(len(domain))]
    
    # 메인루프
    while 1:
        # 이웃 해법의 목록을 생성함
        neighbors = []
        for j in range(len(domain)):
            # 각 방향별로 한 개씩 선택함
            # >>> sol
            # [5, 2, 7, 8, 4, 8, 5, 1, 2, 6]
            # >>> sol[0:0]+[sol[0]-1]+sol[1:]
            # [4, 2, 7, 8, 4, 8, 5, 1, 2, 6]
            # >>> sol[0:0]+[sol[0]+1]+sol[1:]
            # [6, 2, 7, 8, 4, 8, 5, 1, 2, 6]
            if sol[j] > domain[j][0]:
                neighbors.append(sol[0:j]+[sol[j]-1]+sol[j+1:])
            if sol[j] < domain[j][1]:
                neighbors.append(sol[0:j]+[sol[j]+1]+sol[j+1:])
                
        # 이웃 중에 최적 해답을 살펴봄
        current = costf(sol)
        best = current
        for j in range(len(neighbors)):
            cost = costf(neighbors[j])
            if cost < best:
                best = cost
                sol = neighbors[j]
        
        # 개선되지 않으면 최적 해답임
        if best == current:
            break
    
    return sol

#s = hillclimb(domain, schedulecost)
#print schedulecost(s)
#printschedule(s)

def annealingoptimize(domain, costf, T=10000.0, cool=0.95, step=1):
    # 무작위 값으로 초기화함
    vec = [random.randint(domain[i][0], domain[i][1])
           for i in range(len(domain))]
    
    while T > 0.1:
        # 인덱스 중 한개를 선택함
        i = random.randint(0,len(domain)-1)
        
        # 변경할 방향을 선택함
        dir = random.randint(-step, step)
        
        # 변경할 값 중의 하나로 새로운 리스트를 만듦
        vecb = vec[:]
        vecb[i] += dir
        if vecb[i] < domain[i][0]: vecb[i] = domain[i][0]
        elif vecb[i] > domain[i][1]: vecb[i] = domain[i][1]
        
        # 현재 비용과 새로운 비용을 계산함
        ea = costf(vec)
        eb = costf(vecb)
        p = pow(math.e, (-eb-ea)/T)

        print vec,ea
        
        # 더 좋은지, 또는 확률이 차단 기준 이하인지 판단함
        if(eb < ea or random.random() < p):
            vec = vecb
        
        # 온도를 줄임
        T = T*cool
    return vec

#s = annealingoptimize(domain, schedulecost)
#print schedulecost(s)
#printschedule(s)


def geneticoptimize(domain, costf, popsize=50, step=1, mutprob=0.2, elite=0.2, maxiter=100):
    # 돌연변이 연산
    def mutate(vec):
        i = random.randint(0, len(domain)-1)
        if random.random() < 0.5 and vec[i] > domain[i][0]:
            return vec[0:i]+[vec[i]-step]+vec[i+1:]
        elif vec[i] < domain[i][1]:
            return vec[0:i]+[vec[i]+step]+vec[i+1:]
    
    # 교배 연산
    def crossover(r1, r2):
        i = random.randint(1, len(domain)-2)
        return r1[0:i]+r2[i:]
    
    # 초기 개체군을 생성함
    pop = []
    for i in range(popsize):
        vec = [random.randint(domain[i][0], domain[i][1])
               for i in range(len(domain))]
        if vec == None:
            print 'None'
        pop.append(vec)
    
    # 각 세대의 선발된 엘리트 개체군 수를 계산함
    topelite = int(elite*popsize)
    
    # 메인 루프
    for i in range(maxiter):
        scores = [(costf(v), v) for v in pop if v != None]
        scores.sort()
        ranked = [v for (s,v) in scores]
        
        # 생존자들로 시작함
        pop = ranked[0:topelite]
        
        # 생존자에 돌연변이와 번식을 수행함
        while len(pop) < popsize:
            if random.random() < mutprob:
                # 돌연변이
                c = random.randint(0, topelite)
                pop.append(mutate(ranked[c]))
            else:
                # 교배
                c1 = random.randint(0, topelite)
                c2 = random.randint(0, topelite)
                pop.append(crossover(ranked[c1], ranked[c2]))
        # 현재 최고 점수를 출력함
        #print scores[0][0]
    return scores[0][1]

#s = geneticoptimize(domain, schedulecost)
#printschedule(s)

def swarmoptimize(domain,costf,popsize=20,lrate=0.1,maxv=2.0,iters=50):
    # Initialize individuals
    # current solutions
    x=[]
    
    # best solutions
    p=[]
    
    # velocities
    v=[]
    
    for i in range(0,popsize):
        vec=[float(random.randint(domain[i][0],domain[i][1])) 
             for i in range(len(domain))]
        x.append(vec)
        p.append(vec[:])
        v.append([0.0 for i in vec])
        
        
    for ml in range(0,iters):
        for i in range(0,popsize):
            # Best solution for this particle
            if costf(x[i])<costf(p[i]):
                p[i]=x[i][:]
            g=i
            
            # Best solution for any particle
            for j in range(0,popsize):
                if costf(p[j])<costf(p[g]): g=j
            for d in range(len(x[i])):
                # Update the velocity of this particle
                v[i][d]+=lrate*(p[i][d]-x[i][d])+lrate*(p[g][d]-x[i][d])
                
                # constrain velocity to a maximum
                if v[i][d]>maxv: v[i][d]=maxv
                elif v[i][d]<-maxv: v[i][d]=-maxv
                
                # constrain bounds of solutions
                x[i][d]+=v[i][d]
                if x[i][d]<domain[d][0]: x[i][d]=domain[d][0]
                elif x[i][d]>domain[d][1]: x[i][d]=domain[d][1]
                
        print p[g],costf(p[g])
    return p[g]
