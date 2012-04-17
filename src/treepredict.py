#-*- coding: UTF-8 -*-

#my_data = [['slashdot', 'USA', 'yes', 18, 'None'],
#           ['google', 'France', 'yes', 23, 'Premium'],
#           ['digg', 'USA', 'yes', 24, 'Basic'],
#           ['kiwitobes', 'France', 'yes', 23, 'Basic'],
#           ['google', 'UK', 'no', 21, 'Premium'],
#           ['(direct)', 'New Zealand', 'no', 12, 'None'],
#           ['(direct)', 'UK', 'no', 21, 'Basic'],
#           ['google', 'USA', 'no', 24, '{remium'],
#           ['slashdot', 'France', 'yes', 19, 'None'],
#           ['digg', 'USA', 'no', 18, 'None'],
#           ['google', 'UK', 'no', 18, 'None'],
#           ['kiwitobes', 'UK', 'no', 19, 'None'],
#           ['digg', 'New Zealand', 'yes', 12, 'Basic'],
#           ['slashdot', 'UK', 'no', 21, 'None'],
#           ['google', 'UK', 'yes', 18, 'Basic'],
#           ['kiwitobes', 'France', 'yes', 19, 'Basic']]

my_data = [line.strip().split('\t') for line in file('../data/decision_tree_example.txt')]
#print my_data


class decisionnode:
    def __init__(self, col=-1, value=None, results=None, tb=None, fb=None):
        self.col = col
        self.value = value
        self.results = results
        self.tb = tb
        self.fb = fb

# 특정 세로줄을 분리함. 숫자나 명사류 값도 처리함
def divideset(rows, column, value):
    # 가로줄이 첫 번째 그룹(true)에 있는지
    # 두 번째 그룹(false)에 있는지 알려주는 함수를 만듦
    split_function = None
    if isinstance(value, int) or isinstance(value, float):
        split_function = lambda row:row[column] >= value
    else:
        split_function = lambda row:row[column] == value
    
    # 가로줄을 분리해서 두 개의 집합을 만들고 그들을 리턴함
    set1 = [row for row in rows if split_function(row)]
    set2 = [row for row in rows if not split_function(row)]
    return (set1, set2)

#print divideset(my_data, 2, 'yes')[0]
#print divideset(my_data, 2, 'yes')[1]

# 가능한 결과 개수를 셈(각 가로줄의 마지막 세로줄이 결과임)
def uniquecounts(rows):
    results = {}
    for row in rows:
        # 마지막 세로줄에 결과가 있음
        r = row[len(row)-1]
        if r not in results: results[r] = 0
        results[r] += 1
    return results

print 'uniquecounts(my_data) : ', 
print uniquecounts(my_data)


# 무작위로 위치한 항목이 잘못된 분류에 속할 확률
def giniimpurity(rows):
    total = len(rows)
    counts = uniquecounts(rows)
    imp = 0
    for k1 in counts:
        p1 = float(counts[k1]) / total
        for k2 in counts:
            if k1 == k2: continue
            p2 = float(counts[k2]) / total
            imp += p1 * p2
    return imp

# 엔트로피는 모든 다른 결과에 대한 p(x)log(p(x))의 총합임
def entropy(rows):
    from math import log
    log2 = lambda x:log(x) / log(2)
    results = uniquecounts(rows)
    # 이제 엔트로피를 계산함
    ent = 0.0
    for r in results.keys():
        p = float(results[r]) / len(rows)
        ent = ent - p*log2(p)
    return ent

# 결과가 범주형 자료가 아닌 연속형 자료로 나타날 경우
# 단순 분류의 문제가 아니기 때문에 득점 함수에서 숫자의 조밀성을 따져야 한다.
def variance(rows):
    if len(rows) == 0: return 0
    data = [float(row[len(row)-1]) for row in rows]
    mean = sum(data) / len(data)
    variance = sum([(d-mean)**2 for d in data]) / len(data)
    return variance
   
#print giniimpurity(my_data)
#print entropy(my_data)
#set1, set2 = divideset(my_data, 2, 'yes')
#print uniquecounts(set1)
#print uniquecounts(set2)
#print entropy(set1)
#print entropy(set2)
#print giniimpurity(set1)
#print giniimpurity(set2)

def buildtree(rows, scoref=entropy):
    if len(rows) == 0: return decisionnode()
    current_score = scoref(rows)
    
    # 최적 조건을 추적하는 몇 개 변수를 설정함
    best_gain = 0.0
    best_criteria = None
    best_sets = None
    
    column_count = len(rows[0])-1
    for col in range(0, column_count):
        # 이 세로줄 내의 다른 값들의 목록을 생성함
        column_values = {}
        for row in rows:
            column_values[row[col]] = 1
        # 이제 가로줄을 이 세로줄 내의 각 값으로 분리함
        for value in column_values.keys():
            (set1, set2) = divideset(rows, col, value)
            
            # 정보이득
            p = float(len(set1)) / len(rows)
            gain = current_score - p * scoref(set1) - (1 - p) * scoref(set2)
            if gain > best_gain and len(set1) > 0 and len(set2) > 0:
                best_gain = gain
                best_criteria = (col, value)
                best_sets = (set1, set2)
    # 하위 브랜치를 생성함
    if best_gain > 0:
        trueBranch = buildtree(best_sets[0])
        falseBranch = buildtree(best_sets[1])
        return decisionnode(col=best_criteria[0], value=best_criteria[1],
                            tb=trueBranch, fb=falseBranch)
    else:
        return decisionnode(results = uniquecounts(rows))
    
tree = buildtree(my_data)

def printtree(tree, indent=''):
    # 끝 노드인지 확인함
    if tree.results != None:
        print str(tree.results)
    else:
        # 조건을 출력함
        print str(tree.col) + ':' + str(tree.value) + '? '
        
        # 브랜치를 출력함
        print indent + 'T->',
        printtree(tree.tb, indent + '  ')
        print indent + 'F->',
        printtree(tree.fb, indent + '  ')

printtree(tree)

def getwidth(tree):
    if tree.tb == None and tree.fb == None: return 1
    return getwidth(tree.tb) + getwidth(tree.fb)

def getdepth(tree):
    if tree.tb == None and tree.fb == None: return 0
    return max(getdepth(tree.tb), getdepth(tree.fb)) + 1

from PIL import Image, ImageDraw
def drawnode(draw, tree, x, y):
    if tree.results == None:
        # 각 가지의 폭을 얻음
        w1 = getwidth(tree.fb) * 100
        w2 = getwidth(tree.tb) * 100
        
        # 이 노드에 필요한 전체 공간을 결정함
        left = x - (w1 + w2) / 2
        right = x + (w1 + w2) / 2
        
        # 조건 문자열을 그림
        draw.text((x-20, y-10), str(tree.col) + ':' + str(tree.value), (0,0,0))
        
        # 가지에 링크를 그림
        draw.line((x, y, left+w1/2, y+100), fill=(255,0,0))
        draw.line((x, y, right-w2/2, y+100), fill=(255,0,0))
        
        # 가지 노드들을 그림
        drawnode(draw, tree.fb, left+w1/2, y+100)
        drawnode(draw, tree.tb, right-w2/2, y+100)
    else:
        txt = ' \n'.join(['%s:%d'%v for v in tree.results.items()])
        draw.text((x-20, y), txt, (0,0,0))
        
def drawtree(tree, jpeg='tree.jpg'):
    w = getwidth(tree) * 100
    h = getdepth(tree) * 100 + 120
    
    img = Image.new('RGB', (w,h), (255,255,255))
    draw = ImageDraw.Draw(img)
    
    drawnode(draw, tree, w/2, 20)
    img.save(jpeg, 'JPEG')

drawtree(tree, jpeg='../treeview.jpg')

def classify(observation, tree):
    if tree.results != None:
        return tree.results
    else:
        v = observation[tree.col]
        branch = None
        if isinstance(v, int) or isinstance(v, float):
            if v >= tree.value: branch = tree.tb
            else: branch = tree.fb
        else:
            if v >= tree.value: branch = tree.tb
            else: branch = tree.fb
        return classify(observation, branch)

print classify(['(direct)', 'USA', 'yes', 5], tree)

# 과잉적합 피하기 위한 방법
def prune(tree, mingain):
    # 가지가 끝 노드가 아닌 경우 가지 침
    if tree.tb.results == None:
        prune(tree.tb, mingain)
    if tree.fb.results == None:
        prune(tree.fb, mingain)
    
    # 두 하위 가지가 끝 노드가 아닌 경우 병합 가능성을 조사함
    if tree.tb.results != None and tree.fb.results != None:
        # 데이터 세트를 병합함
        tb, fb = [], []
        for v,c in tree.tb.results.items():
            tb += [[v]]*c
        for v,c in tree.fb.results.items():
            fb += [[v]]*c
        # 엔트로피 감소를 조사함
        delta = entropy(tb + fb) - (entropy(tb) + entropy(fb) / 2)
        if delta < mingain:
            # 가지들을 병합함
            tree.tb, tree.fb = None, None
            tree.results = uniquecounts(tb+fb)

prune(tree, 0.1)
printtree(tree)
prune(tree, 1.0)
printtree(tree)

