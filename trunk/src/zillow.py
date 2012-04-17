#-*- coding: UTF-8 -*-

import xml.dom.minidom
import urllib2
import treepredict

zwskey = "X1-ZWz1chwxis15aj_9skq6"

def getaddressdata(address, city):
    escad = address.replace(' ', '+')
    
    # URL 만듦
    url = 'http://www.zillow.com/webservice/GetDeepSearchResults.htm?'
    url += 'zws-id=%s&address=%s&citystatezip=%s' % (zwskey, escad, city)
    
    # 결과로 나온 XML을 파싱함
    doc = xml.dom.minidom.parseString(urllib2.urlopen(url).read())
    code = doc.getElementsByTagName('code')[0].firstChild.data
    
    # 성공이면 0. 그렇지 않으면 오류임
    if code != '0': return None
    
    # 속성 정보를 추출함
    try:
        zipcode = doc.getElementsByTagName('zipcode')[0].firstChild.data
        use = doc.getElementsByTagName('useCode')[0].firstChild.data
        year = doc.getElementsByTagName('yearBuilt')[0].firstChild.data
        bath = doc.getElementsByTagName('bathrooms')[0].firstChild.data
        bed = doc.getElementsByTagName('bedrooms')[0].firstChild.data
        rooms = doc.getElementsByTagName('totalRooms')[0].firstChild.data
        price = doc.getElementsByTagName('amount')[0].firstChild.data
    except:
        return None
    
    return (zipcode, use, int(year), float(bath), int(bed), int(rooms), price)

def getpricelist():
    l1 = []
    for line in file('../data/addresslist.txt'):
        data = getaddressdata(line.strip(), 'Cambridge,MA')
        if data != None:
            l1.append(data)
            print data
    return l1

housedata = getpricelist()
housetree = treepredict.buildtree(housedata, scoref=treepredict.variance)
treepredict.drawtree(housetree, '../housetree.jpg')