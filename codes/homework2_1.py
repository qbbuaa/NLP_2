import jieba
import os
import re
import json
def get_useless(list):
    with open(list, 'r', encoding='utf-8') as file:
        useless = set([line.strip() for line in file.readlines()])
    return useless

def get_texts(texts,rootDir,punctuations,stopwords):
    listdir = os.listdir(rootDir)
    for file in listdir:
        path = os.path.join(rootDir, file)
        if os.path.isfile(path) and os.path.splitext(file)[1].lower() == '.txt':
            with (open(os.path.abspath(path), "r", encoding='ansi') as file):
                filename = os.path.splitext(os.path.basename(file.name))[0]
                if re.search(r'[\u4e00-\u9fa5]', filename):
                    ad = '本书来自www.cr173.com免费txt小说下载站\n更多更新免费电子书请关注www.cr173.com'
                    f = file.read()
                    f = f.replace(ad,'')
                    f = f.replace('\n','')
                    full_width_english = re.compile(r'[\uFF01-\uFF5E]+')
                    f = full_width_english.sub('',f)
                    for punctuation in punctuations :
                        f = f.replace(punctuation, '')
                    words = jieba.lcut(f.replace('\u3000',''))
                    words_noStopWords = [word for word in words if word not in stopwords]
                    texts[filename] = ''.join(words_noStopWords)
        elif os.path.isdir(path):
            get_texts(texts,path, punctuations,stopwords)

if __name__ == '__main__':

    punctuations = get_useless("cn_punctuation.txt")
    stopwords = get_useless("cn_stopwords.txt")

    texts ={}
    rootDir = 'jyxstxtqj_downcc.com'

    get_texts(texts,rootDir,punctuations,stopwords)
    with open('texts.json', 'w') as json_file:
        json.dump(texts, json_file)