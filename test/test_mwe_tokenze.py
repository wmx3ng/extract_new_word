# -*- coding: utf-8 -*-

import nltk

term_item = [('a', 'little', 'or'), ('a', 'little', 'bit'), ('a', 'lot')]
tokenizer = nltk.tokenize.MWETokenizer(term_item, separator=' ')

text = "In a little or , a little bit . or a lot in spite of China."
print(tokenizer.tokenize(text.split()))

tokenizer.add_mwe(('in', 'spite', 'of'))
print(tokenizer.tokenize(text.split()))
