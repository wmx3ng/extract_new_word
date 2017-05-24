# -*- coding:utf-8 -*-

from englory.new_word.cal_new_word.cal.generate_result import GenerateNewWords

data_dirs = ["/home/wong/data/news_list/20170521", "/home/wong/data/news_list/20170522"]
generate_new_word = GenerateNewWords(data_dirs, False, 'nlp', 11112, 1, ['2'])
generate_new_word.set_db_info('mysql-server', 3306, 'root', '', 'recommendation', 'thesaurus')
generate_new_word.set_output_dir('/home/wong/data/output')
generate_new_word.cal()
