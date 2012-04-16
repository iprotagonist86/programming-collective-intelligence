#-*- coding: UTF-8 -*-

import re
import math

def getwords(doc):
    splitter = re.compile('\\W*')
    # 텍스트를 알파멧이 아닌 문자로 분리함
    words = [s.lower() for s in splitter.split(doc)
             if len(s) > 2 and len(s) < 20]
    
    # 유일한 단어들만 리텀
    return dict([(w, 1) for w in words])

def sampletrain(cl):
    cl.train('Nobody owns the water.', 'good')
    cl.train('the quick rabbit jumps fences', 'good')
    cl.train('buy pharmaceuticals now', 'bad')
    cl.train('make quick money at the online casino', 'bad')
    cl.train('the quick brown fox jumps', 'good')
    
class classifier:
    def __init__(self, getfeatures, filename=None):
        # 특성/분류 조합  수를 셈
        self.fc = {}
        
        # 각 분류별 문서 수를 셈
        self.cc = {}
        self.getfeatures = getfeatures
    
    # 특성/분류 쌍 횟수를 증가시킴
    def incf(self, f, cat):
        self.fc.setdefault(f, {})
        self.fc[f].setdefault(cat, 0)
        self.fc[f][cat] += 1
    
    # 분류 횟수를 증가시킴
    def incc(self, cat):
        self.cc.setdefault(cat, 0)
        self.cc[cat] += 1
    
    # 한 특성이 특정 분류에 출현한 횟수
    def fcount(self, f, cat):
        if f in self.fc and cat in self.fc[f]:
            return float(self.fc[f][cat])
        return 0.0
    
    # 분류당 항목 개수
    def catcount(self, cat):
        if cat in self.cc:
            return float(self.cc[cat])
        return 0
    
    # 항목 전체 개수
    def totalcount(self):
        return sum(self.cc.values())
    
    # 전체 분류 목록
    def categories(self):
        return self.cc.keys()
    
    def train(self, item, cat):
        features = self.getfeatures(item)
        # 이 분류 내 모든 특성 횟수를 증가시킴
        for f in features:
            self.incf(f, cat)
        # 이 분류 횟수를 증가시킴
        self.incc(cat)

    def fprob(self, f, cat):
        if self.catcount(cat) == 0: return 0
        
        # 해당 분류에서 특성이 나타난 횟수를 그 분류에 있는 전체 항목 개수로 나눔
        return self.fcount(f, cat) / self.catcount(cat)
    
    def weightedprob(self, f, cat, prf, weight=1.0, ap=0.5):
        # 현재의 확률을 계산함
        basicprob = prf(f, cat)
        
        # 모든 분류에 이 특성이 출현한 횟수를 계산함
        totals = sum([self.fcount(f,c) for c in self.categories()])
        
        # 가중평균을 계산함
        bp = ((weight*ap) + (totals * basicprob)) / (weight + totals)
        return bp

cl = classifier(getwords)
cl.train('the quick brown fox jumps over the lazy dog', 'good')
cl.train('make quick money in the online casino', 'bad')
print cl.fcount('quick', 'good')
print cl.fcount('quick', 'bad')

c = classifier(getwords)
sampletrain(c)
print c.fprob('quick', 'good')

c2 = classifier(getwords)
sampletrain(c2)
print c2.weightedprob('money', 'good', c2.fprob)
sampletrain(c2)
print c2.weightedprob('money', 'good', c2.fprob)


class naivebayes(classifier):
    def __init__(self, getfeatures):
        classifier.__init__(self, getfeatures)
        self.thresholds = {}
    
    def setthreshold(self, cat, t):
        self.thresholds[cat] = t
    
    def getthreshold(self, cat):
        if cat not in self.thresholds: return 1.0
        return self.thresholds[cat]
        
    def docprob(self, item, cat):
        features = self.getfeatures(item)
        
        # 모든 특성의 확률을 곱함
        p = 1
        for f in features: p *= self.weightedprob(f, cat, self.fprob)
        return p
    
    def prob(self, item, cat):
        catprob = self.catcount(cat) / self.totalcount()    # Pr(Categor)
        docprob = self.docprob(item, cat)                   # Pr(Document|Category)
        return docprob * catprob
    
    def classify(self, item, default=None):
        probs = {}
        # 가장 높은 확률을 가진 분류를 찾음
        max = 0.0
        for cat in self.categories():
            probs[cat] = self.prob(item, cat)
            if probs[cat] > max:
                max = probs[cat]
                best = cat
        
        # 확률 값이 threshold * next best를 초과하는지 확인함
        for cat in probs:
            if cat == best: continue
            if probs[cat] * self.getthreshold(best) > probs[best]:
                return default
        return best
    

cl = naivebayes(getwords)
sampletrain(cl)
print cl.prob('quick rabbit', 'good')
print cl.prob('quick rabbit', 'bad')

cl = naivebayes(getwords)
sampletrain(cl)
print cl.classify('quick rabbit', default='unknown')
print cl.classify('quick money', default='unknown')
cl.setthreshold('bad', 3.0)
print cl.classify('quick money', default='unknown')
for i in range(10): sampletrain(cl)
print cl.classify('quick money', default='unknown')


class fisherclassifier(classifier):
    def cprob(self, f, cat):
        # 이 분류 내 이 특성의 빈도
        clf = self.fprob(f, cat)
        if clf == 0: return 0
        
        # 모든 분류에서 이 특성의 빈도
        freqsum = sum([self.fprob(f, c) for c in self. categories()])
        
        # 확률은 이 분류 내 빈도를 전체 빈도로 나눈 값임
        p = clf / freqsum
        
        return p
    
cl = fisherclassifier(getwords)
sampletrain(cl)
print cl.cprob('quick', 'good')
print cl.cprob('money', 'bad')