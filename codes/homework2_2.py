import json
import jieba
import random
import gensim
from gensim import corpora
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import StratifiedKFold
from sklearn.svm import SVC
import numpy as np

def get_bags_and_labels(texts,k,mode,size):
    bags = []
    labels = []
    bags_dic = {}
    for name,text in texts.items():
        if mode == '以“词”为基本单元':
            text = jieba.lcut(text)
        text_l = len(text)
        for i in range(0,text_l, k):
            if i + k < text_l:
                bag = text[i:i + k]
                if mode == '以“字”为基本单元':
                    bag = list(bag)
                if name in bags_dic :
                    bags_dic[name].append(bag)
                else :
                    bags_dic[name] = [bag]
    bags_dic_c = {}
    for name,bags_seperated in bags_dic.items():
        if len(bags_seperated) >= 10:
            bags_dic_c[name] = bags_seperated
    bags_dic.clear()
    bags_l = len(bags_dic_c)
    size_seperateds = {key:(size//bags_l) for key in bags_dic_c.keys()}
    while sum(size_seperateds.values()) < size :
        random_key = random.choice(list(size_seperateds.keys()))
        size_seperateds[random_key] += 1
    compensate = 0
    for name, bags_seperated, size_seperated in zip(bags_dic_c.keys(), bags_dic_c.values(), size_seperateds.values()):
        bags_seperated_l = len(bags_seperated)
        if bags_seperated_l < size_seperated :
            compensate += (size_seperated - bags_seperated_l)
            size_seperateds[name] = bags_seperated_l
    sorted_dict = dict(sorted(bags_dic_c.items(), key=lambda item: len(item[1]),reverse=True))
    for name,bags_seperated in sorted_dict.items():
        if compensate == 0 :
            break
        if len(bags_seperated) >= compensate + size_seperateds[name]:
            size_seperateds[name] += compensate
            compensate = 0
        elif len(bags_seperated) > size_seperateds[name] and len(bags_seperated) < compensate + size_seperateds[name]:
            compensate -= (len(bags_seperated)-size_seperateds[name])
            size_seperateds[name] = len(bags_seperated)
    for name,bags_seperated,size_seperated in zip(bags_dic_c.keys(),bags_dic_c.values(),size_seperateds.values()):
        bags_seperated_l = len(bags_seperated)
        step = bags_seperated_l // size_seperated
        if step == 0 :
            step = 1
        n = 0
        for i in range(0, bags_seperated_l,step):
            n += 1
            bags.append(bags_seperated[i])
            labels.append(name)
            if n >= size_seperated:
                break
    return bags,labels

def get_distribution(ldamodel, bags):
    distributions = []
    for bag in bags:
        bow_vector = ldamodel.id2word.doc2bow(bag)
        distribution = ldamodel.get_document_topics(bow_vector, minimum_probability=0.0)
        array = np.array([second for first, second in distribution])
        distributions.append(array)
    return distributions


def evaluate_classification(distributions, labels):
    cv = StratifiedKFold(n_splits=10, shuffle=True, random_state=42)
    scores = cross_val_score(SVC(), distributions, labels, cv=cv)
    return scores.mean()

if __name__ == '__main__':

    with open('texts.json', 'r') as json_file:
        texts = json.load(json_file)
    ks = [20,100,500,1000,3000]
    ts = [8,16,24,32]
    modes = ['以“词”为基本单元','以“字”为基本单元']
    rates = []
    for k in ks:
        for mode in modes:
            bags,labels = get_bags_and_labels(texts, k, mode, 1000)
            dictionary = corpora.Dictionary(bags)
            corpus = [dictionary.doc2bow(bag) for bag in bags]
            for t in ts:
                ldamodel = gensim.models.LdaMulticore(corpus, num_topics=t, id2word=dictionary, passes=10, workers=2)
                distributions = get_distribution(ldamodel, bags)
                rate = evaluate_classification(distributions, labels)
                rates.append((rate,k,t,mode))
    with open('rates.json', 'w') as json_file:
        json.dump(rates, json_file)