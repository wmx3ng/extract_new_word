# -*- coding:utf-8 -*-
import os
import re
import string
import sys

import nltk

from englory.new_word.cal_new_word.config import Config
from englory.new_word.cal_new_word.config.Config import *
from englory.new_word.cal_new_word.redis_conn.PrefixKeys import *

# english punc pattern.
punc_pattern = re.compile('[' + string.punctuation + ']+')
strip_str = """-“”"""


class InputTokens(object):
    def __init__(self, redis_conn):
        # redis englory_redis_conn, pipeline
        self._redis_conn = redis_conn
        self._pipeline = self._redis_conn.pipeline()
        self._redis_conn.flushdb()
        self._load_stop_words()

    def set_article_list(self, article_list):
        self._article_list = article_list
        self._redis_conn.flushdb()

    def _load_stop_words(self):
        stop_word_path = os.path.join(os.path.dirname(Config.__file__), 'stopWords')
        with open(stop_word_path, "r")as stop_word_read:
            stop_words_id = set(w.strip() for w in stop_word_read.readlines())
            self._stop_words = stop_words_id.union(nltk.corpus.stopwords.words('english'))

    # stat token info.
    def _extract_word_from_list(self, token_list, right):
        if token_list is None or len(token_list) <= 0:
            return

        last_word = token_list[-1]
        # add stat info
        self._pipeline.sadd(set_single_word, last_word)
        self._pipeline.hincrby(single_word, last_word, 1)
        # TODO 熵计算部分目前不考虑
        # if right is not None:
        # add adjoin word
        # self.pipeline.hincrby(adjoin_left_single_word + right, last_word, 1)
        # self.pipeline.hincrby(adjoin_right_single_word + last_word, right, 1)
        # add new word
        real_size = new_word_max_size
        if real_size > len(token_list):
            real_size = len(token_list)
        while real_size > 1:
            word = ' '.join(token_list[- real_size:])
            self._pipeline.hincrby(new_word, word, 1)
            self._pipeline.zincrby(new_word_with_order, word, 1)
            real_size -= 1

        self._extract_word_from_list(token_list[:-1], token_list[-1])

    def _is_punc(self, word):
        if word is None:
            return True
        if len(word) < 4 and punc_pattern.match(word):
            return True
        return False

    def _seg_sent(self, sentence):
        if not sentence:
            return

        tokens = [w.strip(strip_str) for w in nltk.word_tokenize(sentence)]
        token_list = []
        for token in tokens:
            if token == '' or self._is_punc(token) or token in self._stop_words:
                self._extract_word_from_list(token_list, None)
                self._pipeline.hincrby(summary_meta, summary_meta_word_size, len(token_list))
                token_list = []
            else:
                token_list.append(token)
        # handle tail.
        if len(token_list) > 0:
            self._extract_word_from_list(token_list, None)
            self._pipeline.hincrby(summary_meta, summary_meta_word_size, len(token_list))

    def _print_status_info(self, line_no, correct_count, error_count):
        print 'all:', line_no, 'correct count:', correct_count, 'error count:', error_count

    def _get_files_by_channel(self):
        files = []
        for data_dir in self._data_dirs:
            for (dirpath, dirnames, filenames) in os.walk(data_dir):
                files.extend([os.path.join(dirpath, file_name) for file_name in filenames])

        channel_dict = {}
        for file_name in files:
            prefix = file_name.split('.')[0]
            channel_tag = '0'
            if self._by_channel:
                prefix_split = prefix.split('_')
                if len(prefix_split) > 1:
                    channel_tag = prefix_split[-1]

            if channel_tag in channel_dict:
                channel_dict[channel_tag].append(file_name)
            else:
                channel_dict[channel_tag] = [file_name]

        return channel_dict

    def resolve_text(self):
        line_no = 0
        correct_count = 0
        error_count = 0
        for line in self._article_list:
            line_no += 1
            try:
                for sentence in nltk.sent_tokenize(line):
                    self._seg_sent(sentence)

                correct_count += 1
            except Exception, e:
                error_count += 1
                print Exception, ":", e, ":", line
                pass

            if correct_count % 100 == 0:
                self._print_status_info(line_no, correct_count, error_count)
                self._pipeline.execute()

        self._print_status_info(line_no, correct_count, error_count)
        self._pipeline.execute()

    def _cal_ratio(self, partial, words, freq_total, terms, freqs):
        if terms is None or len(terms) == 0 or freqs is None or len(freqs) == 0 or len(terms) != len(freqs):
            return
        dict = {}
        for (term, freq) in zip(terms, freqs):
            dict[term] = int(freq)
        result_list = []
        for word in partial:
            result_list.append(word)
            ratio = 1.0
            tokens = word.split()
            freqs_single_word = [dict[token] for token in tokens]
            for freq in freqs_single_word:
                ratio *= int(freq)

            result = 1.0 * int(words[word]) * (freq_total ** (len(tokens) - 1)) / ratio
            result_list.append(result)

        self._redis_conn.zadd(ratio_new_word_with_order, *result_list)

    def cal_new_word_ratio_with_batch(self):
        words_with_freq = self._redis_conn.hgetall(new_word)
        words = self._redis_conn.zrevrangebyscore(new_word_with_order, sys.maxint, new_word_min_freq, 0, -1, False)
        count_new_word = int(self._redis_conn.hget(summary_meta, summary_meta_word_size))
        window = 1000
        while words:
            partial = words[:window]

            terms = list(set(nltk.flatten([word.split() for word in partial])))
            freqs = self._redis_conn.hmget(single_word, terms)
            self._cal_ratio(partial, words_with_freq, count_new_word, terms, freqs)

            words = words[window:]
