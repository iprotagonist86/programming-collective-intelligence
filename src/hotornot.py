#-*- coding: UTF-8 -*-

import urllib2
import xml.dom.minidom

api_key="479NUNJHETN"

def getrandomrating(c):
    # getRandomProfile용 URL을 생성함
    url = "http://services.hotornot.com/rest/?app_key=%s" % api_key
    url += "&method=Rate.getRandomProfile&retrieve_num=%d" % c
    url += "&get_rate_info=true&meet_users_only=true"
    
    f1 = urllib2.urlopen(url).read()
    doc = xml.dom.minidom.parseString(f1)
    emids = doc.getElementsByTagName('emid')
    ratings = doc.getElementsByTagName('rating')
    
    # emids와 ratings를 결합해서 리스트에 넣음
    result = []
    for e,r in zip(emids, ratings):
        if r.firstChild != None:
            result.append((e.firstChild.data, r.firstChild.data))
    return result

stateregions = {'New England':['ct', 'mn', 'ma', 'nh', 'ri', 'vt'],
                'Mid Atlantic':['de', 'md', 'nj', 'ny', 'pa'],
                'South':['al', 'ak', 'fl', 'ga', 'ky', 'la', 'ms', 'mo', 'nc', 'sc', 'tn', 'va', 'wv'],
                'Midwest':['il', 'in', 'ia', 'ks', 'mi', 'ne', 'nd', 'oh', 'sd', 'wi'],
                'West':['ak', 'ca', 'co', 'hi', 'id', 'mt', 'nv', 'or', 'ut', 'wa', 'wy']}

def getpeopledata(ratings):
    result = []
    for emid, rating in ratings:
        # MeeMe.getProfile 메소드용 URL
        url = "http://services.hotornot.com/rest/?app_key=%s" % api_key
        url += "&method=MeeMe.getProfile&emid=%s&get_keywords=true" % emid
        
        # 이 사람에 대한 정보를 얻음
        try:
            rating = int(float(rating)+0.5)
            doc2 = xml.dom.minidom.parseString(urllib2.urlopen(url).read())
            gender = doc2.getElementsByTagName('gender')[0].firstChild.data
            age = doc2.getElementsByTagName('gender')[0].firstChild.data
            loc = doc2.getElementsByTagName('location')[0].firstChild.data[0:2]
            
            # 주를 거주 지역으로 변경함
            for r,s in stateregions.items():
                if loc in s: region = r
            if region != None:
                result.append((gender, int(age), region, rating))
        except:
            pass
    return result

l1 = getrandomrating(500)
print len(l1)
