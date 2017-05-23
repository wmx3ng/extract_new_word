# -*- coding: utf-8 -*-

import yaml
import nltk

# f = open('test.yaml')
# x = yaml.load(f)
# print x
# # print x.keys()
# # print x.values()
# print x.get('spouse')['name']
# print x.items()
term_item = [('a', 'little', 'or'), ('a', 'little', 'bit'), ('a', 'lot')];
tokenizer = nltk.tokenize.MWETokenizer(term_item, separator=' ')

text = "In a little or , a little bit . or a lot in spite of China."
print tokenizer.tokenize(text.split())

tokenizer.add_mwe(('in', 'spite', 'of'))
print tokenizer.tokenize(text.split())
