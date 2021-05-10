import networkx
import re
from konlpy.tag import Mecab
import math

# Textrank 요약
class TextRank:
    def __init__(self, **kargs):
        self.graph = None
        self.window = kargs.get('window', 5)
        self.coef = kargs.get('coef', 1.0)
        self.threshold = kargs.get('threshold', 0.005)
        self.dictCount = {}
        self.dictBiCount = {}
        self.dictNear = {}
        self.nTotal = 0

    def loadSents(self, sentenceIter, tokenizer=Mecab()):
        def similarity(a, b):
            n = len(a.intersection(b))
            return n / float(len(a) + len(b) - n) / (math.log(len(a) + 1) * math.log(len(b) + 1))

        if not tokenizer: rgxSplitter = re.compile('[\\s.,:;-?!()"\']+')
        sentSet = []
        for sent in filter(None, sentenceIter):
            if type(sent) == str:
                if tokenizer:
                    s = set(filter(None, tokenizer(sent)))
                else:
                    s = set(filter(None, rgxSplitter.split(sent)))
            else:
                s = set(sent)
            # 해당 문장을 토크나이저로 자른 형태들, 2보다 작다면 이는 여기서 NNG, NN, VV, VA을 포함하는 요소가 아예 없거나 하나밖에 없다는 뜻
            if len(s) < 2: continue
            self.dictCount[len(self.dictCount)] = sent
            sentSet.append(s)
            # sentSet : {('아버지', 'NNG'), ('식당', 'NNG')} 등의 형태로 문장의 토큰들을 저장한 곳

        # 모든 문장의 조합에 대해서 similarity 계산 후 dicBiCount에 저장
        for i in range(len(self.dictCount)):
            for j in range(i + 1, len(self.dictCount)):
                s = similarity(sentSet[i], sentSet[j])
                if s < self.threshold: continue
                self.dictBiCount[i, j] = s

    def build(self):
        self.graph = networkx.Graph()
        self.graph.add_nodes_from(self.dictCount.keys())
        for (a, b), n in self.dictBiCount.items():
            self.graph.add_edge(a, b, weight=n * self.coef + (1 - self.coef))

    def rank(self):
        return networkx.pagerank(self.graph, weight='weight')

    def summarize(self, ratio=0.333):
        r = self.rank()
        ks = sorted(r, key=r.get, reverse=True)
        # score = int(len(r)*ratio)

        # 문장 수
        # if score < 3 :
        #    score = len(r)
        # elif score >= 3:
        #    score = 3
        # else:
        #    pass
        score = 3

        ks = ks[:score]
        return ' '.join(map(lambda k: self.dictCount[k], sorted(ks)))

if __name__=='__main__':
    tr = TextRank()
    tagger = Mecab()
    stopword = set([('있', 'VV'), ('하', 'VV'), ('되', 'VV')])
    tr.loadSents(df_copy['original'][0],
                 lambda sent: filter(lambda x: x not in stopword and x[1] in ('NNG', 'NNP', 'VV', 'VA'),
                                     tagger.pos(sent)))
