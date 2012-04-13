#-*- coding: UTF-8 -*-

from PIL import Image, ImageDraw

def readfile(filename):
    lines = [line for line in file(filename)]
    
    # 첫 번째 가로줄은 세로줄 제목임
    colnames = lines[0].strip().split('\t')[1:] # 최좌상단 "Blog"는 뺀다
    rownames = []
    data = []
    for line in lines[1:] :
        p = line.strip().split('\t')
        # 각 가로줄의 첫 번째 세로줄은 가로줄 이름임
        rownames.append(p[0])
        # 가로줄의 나머지 부분이 데이터임
        data.append([float(x) for x in p[1:]])
    
    return rownames, colnames, data


from math import sqrt
def pearson(v1, v2) :
    # 단순 합 계산
    sum1 = sum(v1)
    sum2 = sum(v2)
    
    # 제곱의 합 계산
    sum1Sq = sum([pow(v,2) for v in v1])
    sum2Sq = sum([pow(v,2) for v in v2])
    
    # 곱의 합 계산
    pSum = sum([v1[i] * v2[i] for i in range(len(v1))])
    
    # 피어슨 계수 r 계산 (http://www.vias.org/tmdatanaleng/cc_corr_coeff.html)
    num = pSum - (sum1 * sum2 / len(v1))
    den = sqrt((sum1Sq - pow(sum1, 2)/len(v1)) * (sum2Sq - pow(sum2, 2)/len(v1)))
    if den == 0: return 0
    
    return 1.0 - num/den


def tanamoto(v1, v2):
    c1,c2,shr = 0,0,0
    for i in range(len(v1)):
        if v1[i] != 0: c1 += 1 # v1에만 있는 경우
        if v2[i] != 0: c2 += 1 # v2에만 있는 경우
        if v1[i] != 0 and v2[i] != 0: shr += 1 # 둘 다에 있는 경우
    
    return 1.0 - (float(shr) / (c1 + c2 - shr))


class bicluster:
    def __init__(self, vec, left=None, right=None, distance=0.0, id=None):
        self.left = left
        self.right = right
        self.vec = vec
        self.id = id
        self.distance = distance


def hcluster(rows, distance = pearson):
    distances = {}
    currentclustid = -1
    
    # 초기 군집들을 각 가로줄에서 생성함
    clust = [bicluster(rows[i], id = i) for i in range(len(rows))]
    
    while len(clust) > 1:
        lowestpair = (0,1)
        closest = distance(clust[0].vec, clust[1].vec)
        
        # 가장 작은 거리 값을 가지는 쌍을 찾는 루프
        for i in range(len(clust)):
            for j in range(i+1, len(clust)):
                # distance는 거리 계산 캐시임
                if(clust[i].id, clust[j].id) not in distances:
                    distances[(clust[i].id, clust[j].id)] = distance(clust[i].vec, clust[j].vec)
                d = distances[(clust[i].id, clust[j].id)]
                if d < closest:
                    closest = d
                    lowestpair = (i, j)
        
        # 두 군집 간 평균을 계산함
        mergevec = [(clust[lowestpair[0]].vec[i] + clust[lowestpair[1]].vec[i]) / 2.0
                    for i in range(len(clust[0].vec))]
        
        # 새로운 군집을 생성함
        newcluster = bicluster(mergevec, left = clust[lowestpair[0]],
                               right = clust[lowestpair[1]],
                               distance = closest, id = currentclustid)
        
        # 원래의 집합 안에 포함되지 않은 군집 id들은 음수임
        currentclustid -= 1
        del clust[lowestpair[1]]
        del clust[lowestpair[0]]
        clust.append(newcluster)
    
    return clust[0]


def printclust(clust, labels=None, n=0):
    # 계층구조를 만들기 위해 들여 씀
    for i in range(n): print ' ',
    if clust.id < 0:
        # 음수 id 값은 트리의 브랜치를 뜻함
        print '-'
    else:
        # 양수 id 값은 트리의 종점을 뜻함
        if labels == None: print clust.id
        else: print labels[clust.id]
        
    # 우측과 좌측 브랜치를 출력함
    if clust.left != None: printclust(clust.left, labels=labels, n=n+1)
    if clust.right != None: printclust(clust.right, labels=labels, n=n+1)

########################################
# 계층적 군집화
########################################
blognames, words, data = readfile('../data/myblogdata.txt')
clust = hcluster(data)
printclust(clust, labels=blognames)


def getheight(clust):
    # 종점인 경우 높이는 1임
    if clust.left == None and clust.right == None: return 1
    
    # 그렇지 않으면 높이는 각 브랜치 높이들의 합임
    return getheight(clust.left) + getheight(clust.right)

def getdepth(clust):
    # 종점 거리는 0.0임
    if clust.left == None and clust.right == None: return 0
    
    # 브랜치의 거리는 양쪽 중 큰 것에 자신의 거리를 더한 값임
    return max(getdepth(clust.left), getdepth(clust.right)) + clust.distance

def drawnode(draw, clust, x, y, scaling, labels):
    if clust.id < 0:
        h1 = getheight(clust.left) * 20
        h2 = getheight(clust.right) * 20
        top = y - (h1 + h2) / 2
        bottom = y + (h1 + h2) /2
        # 선 길이
        ll = clust.distance * scaling
        # 이 군집에서 자식들까지 수직선
        draw.line((x, top+h1/2, x, bottom-h2/2), fill=(255,0,0))
        
        # 왼쪽 항목까지 수평선
        draw.line((x, top+h1/2, x+ll, top+h1/2), fill=(255,0,0))
        
        # 오른쪽 항목까지 수평선
        draw.line((x, bottom-h2/2, x+ll, bottom-h2/2), fill=(255,0,0))
        
        # 이 함수로 왼쪽 오른쪽 노드를 그림
        drawnode(draw, clust.left, x+ll, top+h1/2, scaling, labels)
        drawnode(draw, clust.right, x+ll, bottom-h2/2, scaling, labels)
    else:
        # 종점이면 항목 라벨을 그림
        draw.text((x+5, y-7), labels[clust.id], (0,0,0))

   
def drawdendrogram(clust, labels, jpeg='../clusters.jpg'):
    # 높이와 폭
    h = getheight(clust) * 20
    w = 1200
    depth = getdepth(clust)
    
    # 고정 폭에 맞게 비율 조정
    scaling = float(w - 150) / depth
    
    # 흰색 배경의 새로운 이미지 생성
    img = Image.new('RGB', (w,h), (255,255,255))
    draw = ImageDraw.Draw(img)
    
    draw.line((0, h/2, 10, h/2), fill=(255,0,0))
    
    # 첫 번째 노드 그림
    drawnode(draw, clust, 10, (h/2), scaling, labels)
    img.save(jpeg, 'JPEG')

########################################
# 계통도 출력
########################################
#drawdendrogram(clust, blognames, jpeg='../data/blogclust.jpg')


def rotatematrix(data):
    newdata = []
    for i in range(len(data[0])):
        newrow = [data[j][i] for j in range(len(data))]
        newdata.append(newrow)
    return newdata

########################################
# 세로줄 군집화
########################################
#rdata = rotatematrix(data)
#wordclust = hcluster(rdata)
#drawdendrogram(wordclust, labels=words, jpeg='../data/wordclust.jpg')


########################################
# tanamoto coefficient 이용한 군집화
########################################
#wants,people,data = readfile('../data/zebo.txt')
#clust = hcluster(data, distance = tanamoto)
#drawdendrogram(clust, wants)


import random

def kcluster(rows, distance=pearson, k=4):
    # 각 점의 최대, 최소값을 구함
    ranges = [(min([row[i] for row in rows]), max([row[i] for row in rows]))
              for i in range(len(rows[0]))]
    
    # 임의로 선정한 k개의 중심점을 생성함
    clusters = [[random.random() * (ranges[i][1] - ranges[i][0]) + ranges[i][0]
                 for i in range(len(rows[0]))] for j in range(k)]
    
    lastmatches = None
    for t in range(100):
        print 'Iteration %d' % t
        # 각 k번째 리스트에는 해당 클러스터에 들어갈 row의 id들이 들어감
        bestmatches = [[] for i in range(k)]
            
        # 각 가로줄별로 가장 근접한 중심점을 찾음
        for j in range(len(rows)):
            row = rows[j]
            bestmatch = 0
            for i in range(k):
                d = distance(clusters[i], row)
                if d < distance(clusters[bestmatch], row): bestmatch = i
            bestmatches[bestmatch].append(j)
            
        # 이전과 같은 결과라면 완료함
        if bestmatches == lastmatches: break
        lastmatches = bestmatches
        
        # 중심점을 멤버들의 평균으로 이동함
        for i in range(k):
            avgs = [0.0] * len(rows[0])
            if len(bestmatches[i]) > 0:
                # bestmatches[i]에 들어있는 row들을 합산
                for rowid in bestmatches[i]:
                    for m in range(len(rows[rowid])):
                        avgs[m] += rows[rowid][m]
                # 위에서 구한 합산값에서 row들의 개수를 나눠서 평균값 저장
                for j in range(len(avgs)):
                    avgs[j] /= len(bestmatches[i])
                clusters[i] = avgs # clusters[i]에는 각 k 클러스트에 포함되는 평균치가 저장됨
    
    return bestmatches


########################################
# k-means 군집화
########################################
#kclust = kcluster(data, k=10)
#print [blognames[r] for r in kclust[0]]


def scaledown(data, distance=pearson,rate=0.01):
    n = len(data)
    
    # 모든 항목 쌍 간의 실제 거리
    realdist = [[distance(data[i], data[j]) for j in range(n)]
                for i in range(0,n)]
    outersum = 0.0
    
    # 2D 내에서 무작위로 선정된 위치에 시작점을 초기화
    loc = [[random.random(), random.random()] for i in range(n)]
    fakedist = [[0.0 for j in range(n)] for i in range(n)]
    
    lasterror = None
    for m in range(0, 1000):
        # 투영된 거리를 구함
        for i in range(n):
            for j in range(n):
                fakedist[i][j] = sqrt(sum([pow(loc[i][x] - loc[j][x], 2)
                                           for x in range(len(loc[i]))]))
                
        # 점을 이동시킴
        grad = [[0.0, 0.0] for i in range(n)]
        
        totalerror = 0
        for k in range(n):
            for j in range(n):
                if j==k: continue
                # 오류는 거리 간의 차이 비율임
                errorterm = (fakedist[j][k] - realdist[j][k]) / realdist[j][k]
                
                # 각 점을 오류 정도에 비례해서 다른 점 근처나 멀리 이동시킴
                grad[k][0] += ((loc[k][0] - loc[j][0]) / fakedist[j][k]) * errorterm
                grad[k][1] += ((loc[k][1] - loc[j][1]) / fakedist[j][k]) * errorterm
                
                # 전체 오류를 기록함
                totalerror += abs(errorterm)
        print totalerror
        
        # 점들을 움직여 얻은 결과가 더 나쁘면 작업을 마침
        if lasterror and lasterror < totalerror: break
        lasterror = totalerror
        
        # 각 점들을 학습 비율과 기울기를 곱한 만큼 이동시킴
        for k in range(n):
            loc[k][0] -= rate * grad[k][0]
            loc[k][0] -= rate * grad[k][1]
            
    return loc


def draw2d(data, labels, jpeg='../mds2d.jpg'):
    img = Image.new('RGB', (2000, 2000), (255,255,255))
    draw = ImageDraw.Draw(img)
    
    for i in range(len(data)):
        x = (data[i][0] + 0.5) * 1000
        y = (data[i][1] + 0.5) * 1000
        draw.text((x,y), labels[i], (0,0,0))
    img.save(jpeg, 'JPEG')


blognames, words, data = readfile('../data/myblogdata.txt')
coords = scaledown(data)
draw2d(coords, blognames, jpeg='../blogs2d.jpg')