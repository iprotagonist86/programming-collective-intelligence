#-*- coding: UTF-8 -*-

from math import tanh
from pysqlite2 import dbapi2 as sqlite

# activation function(1 / (1 + e^x)) 미분값으로 1 - x^2 을 이용함. 아래 그래프 참고
# http://www.google.co.kr/#hl=ko&lr=lang_ko&newwindow=1&tbs=lr:lang_1ko&sclient=psy-ab&q=1+%2F+(1+%2B+e%5E-x)&oq=1+%2F+(1+%2B+e%5E-x)&aq=f&aqi=g-jCL4&aql=&gs_l=hp.3..0i18i33i19l4.2580l3261l6l4584l2l2l0l0l0l0l203l297l1j0j1l2l0.&pbx=1&bav=on.2,or.r_gc.r_pw.r_qf.,cf.osb&fp=3e5ac889d92f9d66&biw=1355&bih=845
# http://www.google.co.kr/#hl=ko&lr=lang_ko&newwindow=1&tbs=lr:lang_1ko&sclient=psy-ab&q=1+-+x%5E2&oq=1+-+x%5E2&aq=f&aqi=g-jCL1&aql=&gs_l=hp.3..0i18i33i19.358631l364186l7l364356l17l11l5l1l1l1l877l2278l0j9j1j6-1l17l0.&pbx=1&bav=on.2,or.r_gc.r_pw.r_qf.,cf.osb&fp=3e5ac889d92f9d66&biw=1355&bih=845
# 즉, 아래 함수는 쌍곡탄젠트(hyperbolic tangent)가 아니라 그의 미분 함수를 나타낸다.
def dtanh(y):
    return 1.0 - y*y

class searchnet:
    def __init__(self, dbname):
        self.con = sqlite.connect(dbname)
    
    def __del__(self):
        self.con.close()
    
    def maketables(self):
        self.con.execute('drop table hiddennode')
        self.con.execute('drop table wordhidden')
        self.con.execute('drop table hiddenurl')
        self.con.execute('create table hiddennode(create_key)')
        self.con.execute('create table wordhidden(fromid, toid, strength)')
        self.con.execute('create table hiddenurl(fromid, toid, strength)')
        self.con.commit()
    
    def getstrength(self, fromid, toid, layer):
        if layer == 0: table = 'wordhidden'
        else: table = 'hiddenurl'
        res = self.con.execute(
            'select strength from %s where fromid = %d and toid = %d' % (table, fromid, toid)).fetchone()
        if res == None:
            if layer == 0: return -0.2
            if layer == 1: return 0
        return res[0]
    
    def setstrength(self, fromid, toid, layer, strength):
        if layer == 0: table = 'wordhidden'
        else: table = 'hiddenurl'
        res = self.con.execute('select rowid from %s where fromid=%d and toid=%d' % (table, fromid, toid)).fetchone()
        if res == None:
            self.con.execute('insert into %s (fromid, toid, strength) values (%d, %d, %f)' % (table, fromid, toid, strength))
        else:
            rowid = res[0]
            self.con.execute('update %s set strength = %f where rowid = %d' % (table, strength, rowid))
    
    def generatehiddennode(self, wordids, urls):
        if len(wordids) > 3: return None
        # 이 단어 집합으로 이미 노드를 생성했었는지 확인함
        createkey = '_'.join(sorted([str(wi) for wi in wordids]))
        res = self.con.execute("select rowid from hiddennode where create_key='%s'" % createkey).fetchone()
        
        # 없다면 생성함
        if res == None:
            cur = self.con.execute("insert into hiddennode (create_key) values ('%s')" % createkey)
            hiddenid = cur.lastrowid
            # 기본값을 넣음
            for wordid in wordids:
                self.setstrength(wordid, hiddenid, 0, 1.0/len(wordids))
            for urlid in urls:
                self.setstrength(hiddenid, urlid, 1, 0.1)
            self.con.commit()
    
    def getallhiddenids(self, wordids, urlids):
        l1 = {}
        for wordid in wordids:
            cur = self.con.execute('select toid from wordhidden where fromid = %d' % wordid)
            for row in cur: l1[row[0]] = 1
        for urlid in urlids:
            cur = self.con.execute('select fromid from hiddenurl where toid = %d' % urlid)
            for row in cur: l1[row[0]] = 1
        return l1.keys()
    
    def setupnetwork(self, wordids, urlids):
        # 값 리스트들
        self.wordids = wordids
        self.hiddenids = self.getallhiddenids(wordids, urlids)
        self.urlids = urlids
        
        # 노드 출력들
        self.ai = [1.0] * len(self.wordids)
        self.ah = [1.0] * len(self.hiddenids)
        self.ao = [1.0] * len(self.urlids)
        
        # 가중치 행렬 생성함
        self.wi = [[self.getstrength(wordid, hiddenid, 0)
                    for hiddenid in self.hiddenids]
                   for wordid in self.wordids]
        self.wo = [[self.getstrength(hiddenid, urlid, 1)
                    for urlid in self.urlids]
                   for hiddenid in self.hiddenids]
#        print self.wi
#        print self.wo
        
    def feedforward(self):
        # 검색 단어가 유일한 입력임
        for i in range(len(self.wordids)):
            self.ai[i] = 1.0
        
        # 은닉 노드 활성화
        for j in range(len(self.hiddenids)):
            sum = 0.0
            for i in range(len(self.wordids)):
                sum = sum + self.ai[i] * self.wi[i][j]
            self.ah[j] = tanh(sum)
        
        # 출력 노드 활성화
        for k in range(len(self.urlids)):
            sum = 0.0
            for j in range(len(self.hiddenids)):
                sum = sum + self.ah[j] * self.wo[j][k]
            self.ao[k] = tanh(sum)
        
        return self.ao[:]

    def getresult(self, wordids, urlids):
        self.setupnetwork(wordids, urlids)
        return self.feedforward()

    def backPropagate(self, targets, N=0.5): # N이 학습율(에타)인가? 
        # 출력 오류를 계산함
        output_deltas = [0.0] * len(self.urlids)
        for k in range(len(self.urlids)):
            error = targets[k] - self.ao[k] # 여기 순서가 바뀌었기 때문에 가중치 갱신할 때 빼주는 게 아니라 그냥 더하면 된다
            output_deltas[k] = dtanh(self.ao[k]) * error
        
        # 은닉층의 오류를 계산함
        hidden_deltas = [0.0] * len(self.hiddenids)
        for j in range(len(self.hiddenids)):
            error = 0.0
            for k in range(len(self.urlids)):
                error = error + output_deltas[k] * self.wo[j][k]
            hidden_deltas[j] = dtanh(self.ah[j]) * error
        
        # 출력 가중치를 갱신함
        for j in range(len(self.hiddenids)):
            for k in range(len(self.urlids)):
                change = output_deltas[k] * self.ah[j]
                self.wo[j][k] = self.wo[j][k] + N * change
        
        # 입력 가중치를 갱신함
        for i in range(len(self.wordids)):
            for j in range(len(self.hiddenids)):
                change = hidden_deltas[j] * self.ai[i]
                self.wi[i][j] = self.wi[i][j] + N * change
    
    def trainquery(self, wordids, urlids, selectedurl):
        # 필요시 은닉 노드를 생성함
        self.generatehiddennode(wordids, urlids)
        
        self.setupnetwork(wordids, urlids)
        self.feedforward()
        targets = [0.0] * len(urlids)
        targets[urlids.index(selectedurl)] = 1.0
        error = self.backPropagate(targets)
        self.updatedatabase()
        
    def updatedatabase(self):
        # 데이터베이스 값으로 저장함
        for i in range(len(self.wordids)):
            for j in range(len(self.hiddenids)):
                self.setstrength(self.wordids[i], self.hiddenids[j], 0, self.wi[i][j])
        for j in range(len(self.hiddenids)):
            for k in range(len(self.urlids)):
                self.setstrength(self.hiddenids[j], self.urlids[k], 1, self.wo[j][k])
        self.con.commit()
        
        
mynet = searchnet('nn.db')
mynet.maketables()
wWorld, wRiver, wBank = 101, 102, 103
uWorldBank, uRiver, uEarth = 201, 202, 203
mynet.generatehiddennode([wWorld, wBank], [uWorldBank, uRiver, uEarth])
for c in mynet.con.execute('select * from wordhidden'): print c
for c in mynet.con.execute('select * from hiddenurl'): print c

mynet = searchnet('nn.db')
print mynet.getresult([wWorld, wBank], [uWorldBank, uRiver, uEarth])

mynet = searchnet('nn.db')
mynet.maketables()
mynet.trainquery([wWorld, wBank], [uWorldBank, uRiver, uEarth], uWorldBank)
print '한번 학습 후',
print mynet.getresult([wWorld, wBank], [uWorldBank, uRiver, uEarth])
mynet.trainquery([wWorld, wBank], [uWorldBank, uRiver, uEarth], uWorldBank)
mynet.trainquery([wWorld, wBank], [uWorldBank, uRiver, uEarth], uWorldBank)
mynet.trainquery([wWorld, wBank], [uWorldBank, uRiver, uEarth], uWorldBank)
mynet.trainquery([wWorld, wBank], [uWorldBank, uRiver, uEarth], uWorldBank)
mynet.trainquery([wWorld, wBank], [uWorldBank, uRiver, uEarth], uWorldBank)
mynet.trainquery([wWorld, wBank], [uWorldBank, uRiver, uEarth], uWorldBank)
print '여러번 학습 후',
print mynet.getresult([wWorld, wBank], [uWorldBank, uRiver, uEarth])

mynet = searchnet('nn.db')
mynet.maketables()
allurls = [uWorldBank, uRiver, uEarth]
for i in range(30):
    mynet.trainquery([wWorld, wBank], allurls, uWorldBank)
    mynet.trainquery([wRiver, wBank], allurls, uRiver)
    mynet.trainquery([wWorld], allurls, uEarth)
print '학습을 통해 새로운 검색어 bank에 대한 추론 결과'
print 'world, bank', 
print mynet.getresult([wWorld, wBank], allurls)
print 'river, bank', 
print mynet.getresult([wRiver, wBank], allurls)
print 'bank', 
print mynet.getresult([wBank], allurls)