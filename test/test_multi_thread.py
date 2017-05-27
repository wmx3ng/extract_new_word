# -*- coding:utf-8 -*-
import os

from englory.new_word.cal_new_word.data_clean.csv_2_item import CSV2Item
from englory.new_word.cal_new_word.cal.input_tokens import InputTokens

data_dirs = ['/home/wong/data/news_list/tmp_list']
files = []
for data_dir in data_dirs:
    for (dirpath, dirnames, filenames) in os.walk(data_dir):
        files.extend([os.path.join(dirpath, file_name) for file_name in filenames])
print(files)
csv_2_item = CSV2Item()
csv_2_item.set_file_list(files)
articles = csv_2_item.convert()
i = 0
for article in articles:
    print(i, article)
    i += 1
# print 'get tokens...'
# input_tokens = InputTokens()
# input_tokens.set_article_list(articles)
# input_tokens.resolve_text()
