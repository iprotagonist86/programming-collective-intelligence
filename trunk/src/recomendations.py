#-*- coding: UTF-8 -*-

from math import sqrt

critics={'Lisa Rose': {'Lady in the Water': 2.5, 'Snakes on a Plane': 3.5, 'Just My Luck': 3.0, 'Superman Returns': 3.5, 'You, Me and Dupree': 2.5, 'The Night Listener': 3.0},
         'Gene Seymour': {'Lady in the Water': 3.0, 'Snakes on a Plane': 3.5, 'Just My Luck': 1.5, 'Superman Returns': 5.0, 'The Night Listener': 3.0, 'You, Me and Dupree': 3.5},
         'Michael Phillips': {'Lady in the Water': 2.5, 'Snakes on a Plane': 3.0, 'Superman Returns': 3.5, 'The Night Listener': 4.0},
         'Claudia Puig': {'Snakes on a Plane': 3.5, 'Just My Luck': 3.0, 'Superman Returns': 4.0, 'You, Me and Dupree': 2.5, 'The Night Listener': 4.5},
         'Mick LaSlle': {'Lady in the Water': 3.0, 'Snakes on a Plane': 4.0, 'Just My Luck': 2.0, 'Superman Returns': 3.0, 'The Night Listener': 3.0, 'You, Me and Dupree': 2.0},
         'Jack Matthews': {'Lady in the Water': 3.0, 'Snakes on a Plane': 4.0, 'The Night Listener': 3.0, 'Superman Returns': 5.0, 'You, Me and Dupree': 3.5},
         'Toby': {'Snakes on a Plane': 4.5, 'You, Me and Dupree': 1.0, 'Superman Returns': 4.0}}


# person1과 person2의 거리 기반 유사도 점수를 리턴 
def sim_distance(prefs, person1, person2):
    # 공통 항목 목록 추
    si = {}
    for item in prefs[person1]:
        if item in prefs[person2]:
            si[item] = 1
    
    # 공통 평가 항목이 없는 경우 0 리
    if len(si) == 0: return 0
    
    # 모든 차이 값의 제곱을 더
    sum_of_squares = sum([pow(prefs[person1][item] - prefs[person2][item], 2)
                          for item in prefs[person1] if item in prefs[person2]])
    
    return 1 / (1 + sqrt(sum_of_squares))

print
print '유클라디안 점수'
print(sim_distance(critics, 'Lisa Rose', 'Gene Seymour'))


# p1과 p2에 대한 피어슨 상관계수를 리턴
def sim_pearson(prefs, p1, p2):
    # 같이 평가한 항목들의 목록을 구함
    si = {}
    for item in prefs[p1]:
        if item in prefs[p2]: si[item] = 1
    # 요소들의 개수를 구함
    n = len(si)
    
    # 공통 요소가 없으면 0 리턴
    if n == 0: return 0
    
    # 모든 선호도를 합산함
    sum1 = sum([prefs[p1][it] for it in si])
    sum2 = sum([prefs[p2][it] for it in si])
    
    # 제곱의 합을 계산
    sum1Sq = sum([pow(prefs[p1][it], 2) for it in si])
    sum2Sq = sum([pow(prefs[p2][it], 2) for it in si])
    
    # 곱의 합을 계산
    pSum = sum([prefs[p1][it] * prefs[p2][it] for it in si])
    
    # 피어슨 점수 계산
    num = pSum - (sum1 * sum2 / n)
    den = sqrt((sum1Sq - pow(sum1, 2) / n) * (sum2Sq - pow(sum2, 2) / n))
    if den == 0: return 0
    
    r = num / den
    
    return r

print
print '피어슨 점수'
print sim_pearson(critics, 'Lisa Rose', 'Gene Seymour')


# p1과 p2에 대한 Jaccard Coefficient를 리턴
def sim_jaccard(prefs, p1, p2):
    # 같이 평가한 항목들의 목록을 구함
    si = {}
    for item in prefs[p1]:
        if item in prefs[p2]: si[item] = 1
    # 요소들의 개수를 구함
    M11 = len(si)
    
    # 공통 요소가 없으면 0 리턴
    if M11 == 0: return 0
    
    M10 = len(prefs[p1]) - M11
    M01 = len(prefs[p2]) - M11
    
    # Jaccard distance 계산
    J = 1 - (float(M11) / (M01 + M10 + M11))
        
    return J

print
print '자카드 점수'
print sim_jaccard(critics, 'Lisa Rose', 'Gene Seymour')
print sim_jaccard(critics, 'Lisa Rose', 'Michael Phillips')



# 선호도 딕셔너리에서 최적이 상대편들을 구함
# 결과 개수와 유사도 함수는 옵션 사항임
def topMatches(prefs, person, n=5, similarity=sim_pearson):
    scores = [(similarity(prefs, person, other), other)
              for other in prefs if other != person]
    
    # 최고점이 상단에 오도록 목록을 정렬
    scores.sort()
    scores.reverse()
    return scores[0:n]

print
print '나와 유사도가 높은 평론가 목록 (topMatches)'
print topMatches(critics, 'Toby', n=3)
print topMatches(critics, 'Toby', n=3, similarity=sim_jaccard)


# 다른 사람과의 순위의 가중평균값을 이용해서 특정 사람에 추천
def getRecommendations(prefs, person, similarity=sim_pearson):
    totals = {}
    simSums = {}
    for other in prefs:
        # 나와 나를 비교하지 말것
        if other == person: continue
        sim = similarity(prefs, person, other)
        
        # 0 이하 점수는 무시함
        if sim <= 0: continue
        for item in prefs[other]:
            # 내가 보지 못한 영화만 대상
            if item not in prefs[person] or prefs[person][item] == 0:
                # 유사도 * 점수
                totals.setdefault(item, 0)
                totals[item] += prefs[other][item] * sim
                
                # 유사도 합계
                simSums.setdefault(item, 0)
                simSums[item] += sim
                
    # 정규화된 목록 생성
    rankings = [(total / simSums[item], item) for item, total in totals.items()]
    
    # 정렬된 목록 리턴
    rankings.sort()
    rankings.reverse()
    return rankings

print
print '피어슨 점수로 계산한 추천 영화'
print getRecommendations(critics, 'Toby')

print
print '유클라디안 점수로 계산한 추천 영화'
print getRecommendations(critics, 'Toby', similarity=sim_distance)

print
print '자카드 점수로 계산한 추천 영화'
print getRecommendations(critics, 'Toby', similarity=sim_jaccard)

def transformPrefs(prefs):
    result = {}
    for person in prefs:
        for item in prefs[person]:
            result.setdefault(item, {})
            
            # 물건과 사람을 바꿈
            result[item][person] = prefs[person][item]
    return result

movies = transformPrefs(critics)

print movies
print
print 'Superman Returns와 유사한 영화 순위'
print topMatches(movies, 'Superman Returns')


def calculateSimilarItems(prefs, n=10):
    # 가장 유사한 항목들을 가진 항목 딕셔너리를 생성
    result = {}
    
    # 선호도 행렬을 뒤집어 항목 중심 행렬로 변환
    itemPrefs = transformPrefs(prefs)
    c = 0
    for item in itemPrefs:
        # 큰 데이터 세트를 위해 진척 상태를 갱신
        c+=1
        if c%100 == 0: print "%d / %d" % (c, len(itemPrefs))
        
        # 각 항목과 가장 유사한 항목들을 구함
        scores = topMatches(itemPrefs, item, n = n, similarity=sim_distance)
        result[item] = scores
    return result

print
print 'item 항목 별 유사한 항목들의 목록'
itemsim = calculateSimilarItems(critics)
print itemsim


#for person in prefs:
#        for item in prefs[person]:
            
            
def getRecommendedItems(prefs, itemMatch, user):
    userRatings = prefs[user]
    scores = {}
    totalSim = {}
    
    # 이 사용자가 평가한 모든 항목마다 루프를 돔
    for (item, rating) in userRatings.items():
        
        # 이 항목과 유사한 모든 항목마다 루프를 돔
        for (similarity, item2) in itemMatch[item]:
            
            # 이 사용자가 이 항목을 이미 평가했다면 무시함
            if item2 in userRatings: continue
            
            # 유사도와 평가점수 곱의 가중치 합을 계산
            scores.setdefault(item2, 0)
            scores[item2] += similarity * rating
            
            # 모든 유사도 합을 계산
            totalSim.setdefault(item2, 0)
            totalSim[item2] += similarity
            
    # 평균값을 얻기 위해 합계를 가중치 합계로 나눔
    rankings = [(score/totalSim[item], item) for item, score in scores.items()]
    
    # 최고값에서 최저값 순으로 랭킹을 리턴함
    rankings.sort()
    rankings.reverse()
    return rankings

print
print 'Toby에 대한 추천 영화 목록'
print getRecommendedItems(critics, itemsim, 'Toby')


def getRecommendedItems4PurchaseStatistics(prefs, itemMatch, user):
    if user not in prefs: return None
    
    userRatings = prefs[user]
    scores = {}
    cntSim = {}
    
    # 이 사용자가 평가한 모든 항목마다 루프를 돔
    for (item, rating) in userRatings.items():
        
        # 이 항목과 유사한 모든 항목마다 루프를 돔
        for (similarity, item2) in itemMatch[item]:
            
            # 이 사용자가 이 항목을 이미 평가했다면 무시함
            if item2 in userRatings: continue
            
            # 유사도의 총합을 계산 
            scores.setdefault(item2, 0)
            scores[item2] += similarity
            
            # 모든 유사도 합을 계산
            cntSim.setdefault(item2, 0)
            cntSim[item2] += 1
            
    # 평균값을 얻기 위해 합계를 가중치 합계로 나눔
    rankings = [(score/cntSim[item], item) for item, score in scores.items()]
    
    # 최고값에서 최저값 순으로 랭킹을 리턴함
    rankings.sort()
    rankings.reverse()
    return rankings

print
print 'Toby에 대한 추천 영화 목록'
print getRecommendedItems4PurchaseStatistics(critics, itemsim, 'Toby')



########################
# 무비렌즈 데이터 테스트
########################
def loadMovieLens(path='D:\\Program\\eclipse\\workspace\\RecommenderSystems_py\\data\\ml-100k'):
    
    # 영화 제목을 얻음
    movies={}
    for line in open(path+'\\u.item'):
        (id, title) = line.split('|')[0:2]
        movies[id] = title
        
    # 데이터를 로드함
    prefs={}
    for line in open(path+'\\u.data'):
        (user, movieid, rating, ts) = line.split('\t')
        prefs.setdefault(user, {})
        prefs[user][movies[movieid]] = float(rating)
    return prefs

#prefs = loadMovieLens()
#print
#print '임의 사용자의 평가 점수 몇 개 살펴보기'
#print prefs['87']
#
#print
#print '사용자 기반 추천 기법'
#print getRecommendations(prefs, '87')[0:30]
#
#itemsim = calculateSimilarItems(prefs, n=50)
#print
#print '아이템 기반 추천 기법'
#print getRecommendedItems(prefs, itemsim, '87')[0:30]
#
#print
#print '구매이력 아이템 기반 추천 기법'
#print getRecommendedItems4PurchaseStatistics(prefs, itemsim, '87')[0:30]



########################
# 교보문고 데이터 테스트
########################
def loadKyoboData(path='D:\\Program\\eclipse\\workspace\\RecommenderSystems_py\\data\\kyobo_ratings.csv'):
    # 데이터를 로드함
    prefs={}
    for line in open(path):
        (user, bookid, rating) = line.split(',')
        prefs.setdefault(user, {})
        prefs[user][bookid] = float(rating)
    return prefs

def loadKyoboRawData(path='D:\\Program\\eclipse\\workspace\\RecommenderSystems_py\\data\\kyobo_bought_data_before_Dec_uniq.txt'):
    prefs={}
    file = open(path)
    total_cnt = len(file.readlines())
    file.close()
    
    i = 0
    file = open(path)
    for line in file:
        i = i + 1
        print i, " / ", total_cnt
        #print line
        (user, bookids) = line.split('|')
        #print user.strip()
        ids = bookids.split(',')
        for id in ids:
            #print id.strip()
#            print len(user)
#            print len(user.strip())
            prefs.setdefault(user.strip(), {})
            prefs[user.strip()][id.split(':')[0]] = 1
    return prefs

def writeItemSimilarity(itemsim):
    f = file('itemsim.txt', 'w')
    for (item, scores) in itemsim.items():
        str = ""
        #print item
        str_item = '%s|' % (item)
        #print scores
        str_scores = ''
        for score in scores:
            (sim, itm) = score
            str_scores += '%f:%s,' % (sim, itm)
        str_scores = str_scores.rstrip(',')
        #print str_item+str_scores+'\n'
        f.write(str_item + str_scores + '\n')
    f.close()
    
prefs = loadKyoboRawData()


print
print '임의 사용자의 평가 점수 몇 개 살펴보기'
print prefs['06032402356']

print
print '사용자 기반 추천 기법'
print getRecommendations(prefs, '06032402356')[0:30]

def predict_user_based(path='D:\\Program\\eclipse\\workspace\\RecommenderSystems_py\\data\\dec_u_i.txt'):
    # 데이터를 로드함
    f = file('result.txt', 'w')
    hit = 0
    total_cnt = 0
    for line in open(path):
        total_cnt += 1
        (user, bookid) = line.split()
        print user
        result = getRecommendations(prefs, user)
        if(result == None): continue
        result = result[0:30]
        #print result
        for (sim, item) in result:
            #print sim
            #print item 
            if(item == bookid):
                hit+=1
                f.write('%s|%s|%s' % (user, item, result))
    print hit, "/", total_cnt
    f.close()

predict_user_based()
print "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%"



itemsim = calculateSimilarItems(prefs, n=50)
writeItemSimilarity(itemsim)

#print
#print '아이템 기반 추천 기법'
#print getRecommendedItems(prefs, itemsim, '06032402356')[0:30]

print
print '구매이력 아이템 기반 추천 기법'
print getRecommendedItems4PurchaseStatistics(prefs, itemsim, '06032402356')[0:30]

def predict_item_based(path='D:\\Program\\eclipse\\workspace\\RecommenderSystems_py\\data\\dec_u_i.txt'):
    # 데이터를 로드함
    f = file('result.txt', 'w')
    hit = 0
    total_cnt = 0
    for line in open(path):
        total_cnt += 1
        (user, bookid) = line.split()
        print user
        result = getRecommendedItems4PurchaseStatistics(prefs, itemsim, user)
        if(result == None): continue
        result = result[0:30]
        #print result
        for (sim, item) in result:
            #print sim
            #print item 
            if(item == bookid):
                hit+=1
                f.write('%s|%s|%s' % (user, item, result))
    print hit, "/", total_cnt
    f.close()

predict_item_based()














