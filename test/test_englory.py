# -*- coding:utf-8 -*-
import datetime

from englory.new_word.data_clean.csv_2_item import CSV2Item
from englory.new_word.cal_new_word.cal.input_tokens import InputTokens
from englory.new_word.cal_new_word.cal.generate_result import GenerateNewWords

date_format = '%Y%m%d'
print datetime.datetime.now().strftime(date_format)
csv_2_item = CSV2Item('/home/wong/data/news_list/20170521', '/home/wong/data/output')
csv_2_item.convert()

input_token = InputTokens('/home/wong/data/output', 'nlp', 11112, 1)
input_token.resolve_text()
input_token.cal_new_word_ratio_with_batch()

generate_new_word = GenerateNewWords('nlp', 11112, 1)
generate_new_word.set_db_info('mysql-server', 3306, 'root', '', 'recommendation', 'thesaurus')
generate_new_word.save_2_db()
generate_new_word.set_output_dir('/home/wong/data/output')
generate_new_word.save_2_csv()