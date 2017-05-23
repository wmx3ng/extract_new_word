# -*- coding:utf-8 -*-
import os
import re
import string
import sys

import nltk

from englory.new_word.cal_new_word.config import Config
from englory.new_word.cal_new_word.config.Config import *
from englory.new_word.cal_new_word.redis_conn.PrefixKeys import *
from englory.new_word.cal_new_word.redis_conn.RedisConn import RedisConn

# english punc pattern.
punc_pattern = re.compile('[' + string.punctuation + ']+')
strip_str = """-“”"""


class InputTokens(object):
    def __init__(self, input_dir, redis_host, redis_port, redis_db):
        self.input_dir = input_dir
        # redis englory_redis_conn, pipeline
        self.redis_conn = RedisConn.redis_conn(redis_host, redis_port, redis_db)
        self.redis_conn.flushdb()
        self.pipeline = self.redis_conn.pipeline()

    # stat token info.
    def _extract_word_from_list(self, token_list, right):
        if token_list is None or len(token_list) <= 0:
            return

        last_word = token_list[-1]
        # add stat info
        self.pipeline.sadd(set_single_word, last_word)
        self.pipeline.hincrby(single_word, last_word, 1)
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
            self.pipeline.hincrby(new_word, word, 1)
            self.pipeline.zincrby(new_word_with_order, word, 1)
            real_size -= 1

        self._extract_word_from_list(token_list[:-1], token_list[-1])

    def _is_punc(self, word):
        if word is None:
            return True
        if len(word) < 4 and punc_pattern.match(word):
            return True
        return False

    def _seg_sent(self, sentence, stop_words):
        if not sentence:
            return

        tokens = [w.strip(strip_str) for w in nltk.word_tokenize(sentence)]
        token_list = []
        for token in tokens:
            if token == '' or self._is_punc(token) or token in stop_words:
                self._extract_word_from_list(token_list, None)
                self.pipeline.hincrby(summary_meta, summary_meta_word_size, len(token_list))
                token_list = []
            else:
                token_list.append(token)
        # handle tail.
        if len(token_list) > 0:
            self._extract_word_from_list(token_list, None)
            self.pipeline.hincrby(summary_meta, summary_meta_word_size, len(token_list))

    def resolve_text(self):
        input_path = os.path.join(self.input_dir, 'news')
        stop_word_path = os.path.join(os.path.dirname(Config.__file__), 'stopWords')
        with open(input_path, 'r') as text_read, open(stop_word_path, "r")as stop_word_read:
            lines = text_read.readlines()
            stop_words = set(w.strip() for w in stop_word_read.readlines())

            line_no = 0
            correct_count = 0
            error_count = 0
            for line in lines:
                line_no += 1
                try:
                    for sentence in nltk.sent_tokenize(line):
                        self._seg_sent(sentence, stop_words)

                    correct_count += 1
                except Exception, e:
                    error_count += 1
                    print Exception, ":", e, ":", line
                    pass

                if correct_count % 100 == 0:
                    print line_no, correct_count, error_count
                    self.pipeline.execute()

        self.pipeline.execute()

        cmd = 'rm ' + input_path
        os.system(cmd)

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

        print len(result_list), ",", result_list
        self.redis_conn.zadd(ratio_new_word_with_order, *result_list)

    def cal_new_word_ratio_with_batch(self):
        words_with_freq = self.redis_conn.hgetall(new_word)
        words = self.redis_conn.zrevrangebyscore(new_word_with_order, sys.maxint, new_word_min_freq, 0, -1, False)
        count_new_word = int(self.redis_conn.hget(summary_meta, summary_meta_word_size))
        window = 1000
        while words is not None and len(words) != 0:
            partial = words[:window]

            terms = list(set(nltk.flatten([word.split() for word in partial])))
            freqs = self.redis_conn.hmget(single_word, terms)
            self._cal_ratio(partial, words_with_freq, count_new_word, terms, freqs)

            words = words[window:]
