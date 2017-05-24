# -*- coding:utf-8 -*-
import csv
import re

from remove_html_tag import filter_tags


class CSV2Item(object):
    def __init__(self):
        pass

    def __init__(self, file_list):
        self._file_list = file_list

    def set_file_list(self, file_list):
        self._file_list = file_list

    def _filter_by_len(self, text):
        if not text:
            return None

        new_text = text.replace('\n', ' ').strip()
        if len(new_text) < 60:
            # print 'str_len:', len(new_text)
            return None
        terms = new_text.split()
        if len(terms) < 20:
            # print 'term_len:', len(terms)
            return None

        return new_text

    def convert(self):
        article_set = set()
        for file_path in self._file_list:
            print 'handing ', file_path
            with open(file_path, 'rb') as csvfile:
                spam_reader = csv.reader((line.replace('\0', '').replace('\n', ' ').strip() for line in csvfile),
                                         delimiter=',')
                for row in spam_reader:
                    pure = self._filter_by_len(filter_tags(row[3]))
                    if pure:
                        pure = re.sub(r'[^\x00-\x7F]+', ' ', pure)
                        article_set.add(pure)

        return list(article_set)
