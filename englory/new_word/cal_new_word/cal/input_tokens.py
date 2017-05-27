# -*- coding:utf-8 -*-
import os
import re
import string

import nltk

from englory.new_word.cal_new_word.config import Config
from englory.new_word.cal_new_word.config.Config import *

# english punc pattern.
punc_pattern = re.compile('[' + string.punctuation + ' ]+')
football_score_pattern = re.compile('\d+-\d+')
special_punc_pattern = re.compile('.*[' + """!"#%&'()*,:;<=>?@[\]^_`{|}~""" + ']+.*')

strip_str = """-“”"""


class InputTokens(object):
    def __init__(self):
        self._load_stop_words()
        self._clear()

    def _clear(self):
        self._line_num = 0
        self._correct_num = 0
        self._except_num = 0

        self._dict_single_word = {}
        self._dict_word_group = {}
        self._dict_new_word_ratio = {}
        self._text_len = 0

    def set_article_list(self, article_list):
        self._article_list = article_list
        self._clear()

    def _load_stop_words(self):
        stop_word_path = os.path.join(os.path.dirname(Config.__file__), 'stopWords')
        with open(stop_word_path, "r")as stop_word_read:
            stop_words_id = set(w.strip() for w in stop_word_read.readlines() if not w.startswith('#'))
            self._stop_words = stop_words_id.union(nltk.corpus.stopwords.words('english'))

    # stat token info.
    def _extract_word_from_list(self, token_list, right):
        if token_list is None or len(token_list) <= 0:
            return

        last_word = token_list[-1]
        # add single word
        if last_word in self._dict_single_word:
            self._dict_single_word[last_word] = 1 + self._dict_single_word[last_word]
        else:
            self._dict_single_word[last_word] = 1

        # add new word
        real_size = new_word_max_size
        if real_size > len(token_list):
            real_size = len(token_list)
        while real_size > 1:
            word_group = ' '.join(token_list[- real_size:])
            if word_group in self._dict_word_group:
                self._dict_word_group[word_group] = 1 + self._dict_word_group[word_group]
            else:
                self._dict_word_group[word_group] = 1

            real_size -= 1

        self._extract_word_from_list(token_list[:-1], token_list[-1])

    def _is_punc(self, word):
        if word is None:
            return True
        if punc_pattern.fullmatch(word):
            return True
        return False

    def _is_perfect_token(self, token):
        if not token:
            return False
        # remove the word consist with punc.
        if self._is_punc(token):
            return False
        # remove the football score.
        if football_score_pattern.match(token):
            return False
        # remove contain special punc.
        if special_punc_pattern.match(token):
            return False
        # remove stopwords.
        if token.lower() in self._stop_words:
            return False

        return True

    def _seg_sent(self, article):
        if not article:
            return

        try:
            tokens = [w.strip(strip_str) for w in nltk.word_tokenize(article)]
            if not tokens:
                return

            continuous_token_list = []
            for token in tokens:
                if not self._is_perfect_token(token):
                    self._extract_word_from_list(continuous_token_list, None)
                    self._text_len += len(continuous_token_list)
                    continuous_token_list = []
                else:
                    continuous_token_list.append(token)

            # handle tail.
            if continuous_token_list:
                self._extract_word_from_list(continuous_token_list, None)
                self._text_len += len(continuous_token_list)

            self._correct_num += 1
        except Exception:
            print(Exception, article)
            self._except_num += 1
        finally:
            self._line_num += 1

    def _print_status_info(self, line_no, correct_count, error_count):
        print('all:', line_no, 'correct count:', correct_count, 'error count:', error_count)

    def resolve_text(self):
        for article in self._article_list:
            self._seg_sent(article)

        self._print_status_info(self._line_num, self._correct_num, self._except_num)
        self._cal_new_word_ratio_with_batch()
        return (self._dict_single_word, self._dict_word_group, self._dict_new_word_ratio)

    def _cal_new_word_ratio_with_batch(self):
        for k, v in self._dict_word_group.items():
            if v > new_word_min_freq:
                ratio = 1.0
                tokens = k.split()
                freqs_single_word = [self._dict_single_word[token] for token in tokens]
                for freq in freqs_single_word:
                    ratio *= int(freq)

                result = 1.0 * int(self._dict_word_group[k]) * (self._text_len ** (len(tokens) - 1)) / ratio
                if result > 5000:
                    self._dict_new_word_ratio[k] = result
