#-*- coding: UTF-8 -*-

from random import random, randint
import math

def wineprice(rating, age):
    peak_age = rating - 50
    
    # 등급에 따라 가격을 계산함
    price = rating/2
    if age > peak_age:
        # 최적 연도가 지나면 5년 단위로 가격이 저하됨
        price = price * (5 - (age - peak_age)/2)
    else:
        # 최적 연도에 근접하면 원래 가격의 5배까지 증가함
        price = price * (5 * ((age+1)/peak_age))
    if price < 0: price = 0
    return price

def wineset1():
    rows = []
    for i in range(300):
        # 무작위로 나이(숙성 기간)와 등급을 생성함
        rating = random() * 50 + 50
        age = random() * 50
        
        # 가격을 얻음
        price = wineprice(rating, age)
        
        # 노이즈를 부가함
        price *= (random()*0.2+0.9)
        
        # 데이터 세트에 추가함
        rows.append({'input':(rating, age), 'result':price})
    return rows

def wineset2():
    rows = []
    for i in range(300):
        # 무작위로 나이(숙성 기간)와 등급을 생성함
        rating = random() * 50 + 50
        age = random() * 50
        aisle = float(randint(1, 20))
        bottlesize = [375.0, 750.0, 1500.0][randint(0, 2)]
        
        # 가격을 얻음
        price = wineprice(rating, age)
        price *= (bottlesize/750)
        
        # 노이즈를 부가함
        price *= (random()*0.2+0.9)
        
        # 데이터 세트에 추가함
        rows.append({'input':(rating, age, aisle, bottlesize), 'result':price})
    return rows

print wineprice(95.0, 3.0)
print wineprice(95.0, 8.0)
print wineprice(99.0, 1.0)
data = wineset1()
print data[0]
print data[1]

def euclidean(v1, v2):
    d = 0.0
    for i in range(len(v1)):
        d += (v1[i]-v2[i])**2
    return math.sqrt(d)

def getdistances(data, vec1):
    distancelist = []
    for i in range(len(data)):
        vec2 = data[i]['input']
        distancelist.append((euclidean(vec1, vec2), i))
    distancelist.sort()
    return distancelist

def knnestimate(data, vec1, k=5):
    # 정렬된 거리들을 얻음
    dlist = getdistances(data, vec1)
    avg = 0.0
    
    # 상위 k개 결과의 평균을 구함
    for i in range(k):
        idx = dlist[i][1]
        avg += data[idx]['result']
    avg = avg/k
    return avg

print knnestimate(data, (95.0, 3.0))
print knnestimate(data, (99.0, 3.0))
print knnestimate(data, (99.0, 5.0))
print '실제 가격 : ',
print wineprice(99.0, 5.0) # 실제 가격을 구함
print 'knn (k=3) : ',
print knnestimate(data, (99.0, 5.0), k=3)
print 'knn (k=5) : ',
print knnestimate(data, (99.0, 5.0), k=5)

def inverseweight(dist, num=1.0, const=0.1):
    return num/(dist+const)

def subtractweight(dist, const=1.0):
    if dist > const:
        return 0
    else:
        return const - dist

# http://www.google.co.kr/#hl=ko&newwindow=1&sclient=psy-ab&q=e%5E(-x%5E2+%2F+(2*(10%5E2)))&oq=e%5E(-x%5E2+%2F+(2*(10%5E2)))&aq=f&aqi=&aql=&gs_nf=1&gs_l=hp.3...13365.16778.4.17506.4.4.0.0.0.0.267.699.0j3j1.4.0.l5wvTeROOYE&pbx=1&bav=on.2,or.r_gc.r_pw.r_qf.,cf.osb&fp=72906ba8902e4db5
def gaussian(dist, sigma=5.0):
    return math.e**(-dist**2/(2*sigma**2))

print subtractweight(0.1)
print inverseweight(0.1)
print gaussian(0.1)
print subtractweight(1.0)
print inverseweight(1.0)
print gaussian(1.0)
print gaussian(3.0)

def weightedknn(data, vec1, k=5, weightf=gaussian):
    # 거리를 구함
    dlist = getdistances(data, vec1)
    avg = 0.0
    totalweight = 0.0
    
    # 가중평균을 구함
    for i in range(k):
        dist = dlist[i][0]
        idx = dlist[i][1]
        weight = weightf(dist)
        avg += weight * data[idx]['result']
        totalweight += weight
    if totalweight==0: return 0
    avg = avg / totalweight
    return avg

print 'weightedknn : ',
print weightedknn(data, (99.0, 5.0))
print '실제 가격 : ',
print wineprice(99.0, 5.0) # 실제 가격을 구함

def dividedata(data, test=0.05):
    trainset = []
    testset = []
    for row in data:
        if random() < test:
            testset.append(row)
        else:
            trainset.append(row)
    return trainset, testset

def testalgorithm(algf, trainset, testset):
    error = 0.0
#    print '==========================='
    for row in testset:
        guess = algf(trainset, row['input'])
        error += (row['result'] - guess)**2
#        print guess, row['result'], error
    return error/len(testset)

def crossvalidate(algf, data, trials=100, test=0.05):
    error = 0.0
    for i in range(trials):
        trainset, testset = dividedata(data, test)
        error += testalgorithm(algf, trainset, testset)
    return error/trials

#print 'crossvalidate : ',
#print crossvalidate(knnestimate, data)

def knn3(d, v): return knnestimate(d, v, k=3)
def knn1(d, v): return knnestimate(d, v, k=1)
#print 'knn3 crossvalidate : ',
#print crossvalidate(knn3, data)
#print 'knn1 crossvalidate : ',
#print crossvalidate(knn1, data)
#print 'weighted knn5 crossvalidate : ',
#print crossvalidate(weightedknn, data)
#def knninverse(d,v):
#    return weightedknn(d,v,weightf=inverseweight)
#print 'weighted knn5_inverse crossvalidate : ',
#print crossvalidate(knninverse, data)
#
#data = wineset2()
#print 'wineset2_knn3 : ',
#print crossvalidate(knn3, data)
#print 'wineset2_weighted_knn : ',
#print crossvalidate(weightedknn, data)


def rescale(data, scale):
    scaleddata = []
    for row in data:
        scaled = [scale[i] * row['input'][i] for i in range(len(scale))]
        scaleddata.append({'input':scaled, 'result':row['result']})
    return scaleddata

data1 = wineset1()
data2 = wineset2()
sdata = rescale(data2,[10, 10, 0, 0.5])

#print 'wineset2_scaled_knn : ',
#print crossvalidate(knn3, sdata)
#print 'wineset2_scaled_weighted_knn : ',
#print crossvalidate(weightedknn, sdata)

def createcostfunction(algf, data):
    def costf(scale):
        sdata = rescale(data, scale)
        return crossvalidate(algf, sdata, trials=20)
    return costf

weightdomain = [(0, 20)] * 4

import optimization
data = wineset2()
#costf = createcostfunction(knnestimate, data)
#print 'annealingoptimize로 최적 weight 구하기',
#print optimization.annealingoptimize(weightdomain, costf, step=2)
#print 'geneticoptimize로 최적 weight 구하기',
#print optimization.geneticoptimize(weightdomain, costf)
#print 'swarmoptimize로 최적 weight 구하기',
#print optimization.swarmoptimize(weightdomain, costf, popsize=5, lrate=1, maxv=4, iters=20)

def wineset3():
    rows = wineset1()
    for row in rows:
        if random() < 0.5:
            # 이 와인을 할인점에서 구매함
            row['result'] *= 0.6
    return rows

data = wineset3()
print wineprice(99.0, 20.0),
print 'vs',
print weightedknn(data, [99.0, 20.0])

# 이 함수 뭔가 잘못 구현된 듯 하다.
# range를 k로 잡고 for문을 도는 것도 이상하고
# 확률을 가중치로 구하는 것도 이상하고
def probguess(data,vec1,low,high,k=10,weightf=gaussian):
    dlist=getdistances(data,vec1)
    nweight=0.0
    tweight=0.0
    tmp = 0.0
    ttmp = 0.0
    
    for i in range(k):
        dist=dlist[i][0]
        idx=dlist[i][1]
        weight=weightf(dist)
        v=data[idx]['result']
        
        # 범위 안에 있는가?
        if v>=low and v<=high:
            nweight+=weight
            tmp+=1
        tweight+=weight
        ttmp+=1
    if tweight==0: return 0
    
    # 확률은 범위 내의 가중치를 모든 가중치로 나눈 값임
    # 근데 사실 이렇게 할 필요 없음. 아래 두 값 똑같음.
    # print tmp/ttmp
    # print nweight/tweight
    return nweight/tweight

print '0-40 : ', 
print probguess(data, [99, 20], 0, 40)
print '40-80 : ', 
print probguess(data, [99, 20], 40, 80)
print '80-120 : ',
print probguess(data, [99, 20], 80, 120)
print '120-1000 : ',
print probguess(data, [99, 20], 120, 1000)
print '0-1000 : ',
print probguess(data, [99, 20], 30, 120)

from pylab import *
import numpy

a = array([1,2,3,4])
b = array([4,2,3,1])
#plot(a,b)
#show()
t1 = arange(0.0, 10.0, 0.1)
#plot(t1, sin(t1))
#show()

def cumulativedistributiongraph(data, vec1, high, k=5, weightf=gaussian):
    t1 = arange(0.0, high, 0.1)
    cprob = array([probguess(data, vec1, 0, v, k, weightf) for v in t1])
    plot(t1, cprob)
#    show()

def probabilitydensitygraph(data, vec1, high, k=5, weightf=gaussian):
    t1 = arange(0.0, high, 0.1)
    cprob = array([probguess(data, vec1, v, v+0.1, k, weightf) for v in t1])
    plot(t1, cprob)
#    show()

cumulativedistributiongraph(data, [99.0, 20.0], 120)
probabilitydensitygraph(data, [99.0, 20.0], 120)

def probabilitygraph(data, vec1, high, k=5, weightf=gaussian, ss=5.0):
    # 가격 범위를 생성함
    t1 = arange(0.0, high, 0.1)
    
    # 전체 범위의 확률을 구함
    probs=[probguess(data,vec1,v,v+0.1,k,weightf) for v in t1]
    
    # 주변 확률들의 가우스 값을 더하여 부드럽게 함
    # 이것도 약간 의심스러운데... 
    smoothed=[]
    for i in range(len(probs)):
        sv=0.0
        for j in range(0,len(probs)):
            dist=abs(i-j)*0.1
            weight=gaussian(dist,sigma=ss)
            sv+=weight*probs[j]
        smoothed.append(sv)
    smoothed=array(smoothed)
      
    plot(t1,smoothed)
    show()

probabilitygraph(data, [90, 20], 120)

