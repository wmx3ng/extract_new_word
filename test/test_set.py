# -*- coding:utf-8 -*-
import nltk

s_w = set()
s_w.add('a')
print s_w
print type(s_w)
s_w=s_w.union(nltk.corpus.stopwords.words('english'))
for i in s_w:
    print i
