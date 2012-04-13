#-*- coding: UTF-8 -*-

import feedparser
import re


# 한 RSS 피드 안에 있는 제목과 단어 출현 회수 딕셔너리를 리턴함
def getwordcounts(url):
    # 피드를 파싱함
    d=feedparser.parse(url)
    wc={}
    #print d.entries
    
    # 모든 게시글 별로 루프를 돔
    for e in d.entries:
        #print e
        if 'summary' in e: summary=e.summary
        else : summary=e.description
        #print summary
        
        # 단어 목록을 추출함
        words=getwords(e.title+' '+summary) # 블로그 포스팅 글 제목과 summary에서 추출
        #print words
        for word in words:
            wc.setdefault(word, 0)
            wc[word] += 1
    #print d.feed.title

    # 해당 feed의 title과 해당 feed에 존재하는 모든 블로그 글에 대해 counting 한 데이터
    return d.feed.title, wc 


def getwords(html):
    # 모든 HTML 태그를 제거함
    txt=re.compile(r'<[^>]+>').sub('', html)
    #print txt
    # 비-알파벳 문자들로 단어를 분리함
    words = re.compile(r'[^A-Z^a-z]+').split(txt)
    # 소문자로 변환함
    return [word.lower() for word in words if word != '']


apcount={}
wordcounts={}
feedlist=[ ]
for feedurl in file('./data/feedlist.txt'):
    print feedurl
    test = feedparser.parse(feedurl)
    if len(test.entries) == 0 :
        continue

    feedlist.append(feedurl)
    title,wc = getwordcounts(feedurl)
    wordcounts[title] = wc
    #print wc
    for word, count in wc.items():
        #print word, count
        apcount.setdefault(word, 0)
        if count > 1:
            apcount[word] += 1

wordlist = []   # 집계에 사용할 word list
for w, bc in apcount.items():
    frac = float(bc) / len(feedlist)
    # 전체 블로그 feed list에서 해당 word가 나오는 블로그의 개수(bc)가 10% 이상 50% 미만이면 추가 
    if frac > 0.1 and frac < 0.5 : wordlist.append(w)
    
out = file('./data/myblogdata.txt', 'w')
out.write('Blog')
for word in wordlist : out.write('\t%s' % word)
out.write('\n')
for blog,wc in wordcounts.items():
    out.write(blog)
    for word in wordlist:
        if word in wc : out.write('\t%d' % wc[word])
        else : out.write('\t0')
    out.write('\n')
    
