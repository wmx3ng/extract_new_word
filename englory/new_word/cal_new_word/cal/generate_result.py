# -*- coding:utf-8 -*-
import csv
import datetime
import math
import os
import sys
from enum import Enum

import pymysql as MySQLdb

from englory.new_word.cal_new_word.config.Config import *
from englory.new_word.cal_new_word.config.Config import time_format, time_format_mysql, print_format, contain_format, \
    write_db_winow
from englory.new_word.cal_new_word.redis_conn.PrefixKeys import *
from englory.new_word.cal_new_word.redis_conn.RedisConn import RedisConn

phrase_type = Enum('phrase', 'single')


class GenerateNewWords(object):
    def __init__(self, redis_host, redis_port, redis_db):
        self._merge_words = []
        self._dict_by_freq = {}
        self._dict_by_ratio = {}
        # redis englory_redis_conn, pipeline
        self._redis_conn = RedisConn.redis_conn(redis_host, redis_port, redis_db)
        self._pipeline = self._redis_conn.pipeline()

    def set_output_dir(self, output_dir):
        self._output_dir = output_dir

    def set_db_info(self, db_host, db_port, db_user, db_passwd, db_name, db_table):
        self._db_table = db_table
        self._db_conn = MySQLdb.connect(
            host=db_host,
            port=db_port,
            user=db_user,
            passwd=db_passwd,
            db=db_name,
            charset='utf8'
        )

    def _merge_new_word(self, words, freq):
        if not words or not freq:
            return []

        words_sort = sorted(words, lambda x, y: cmp(len(x), len(y)), reverse=True)
        new_word_dict = {}
        for w in words_sort:
            # merge uppercase and lowercase. and select the bigger one by freq.
            if w.lower() in new_word_dict:
                old_can_word = new_word_dict[w.lower()]
                if freq[w] > freq[old_can_word]:
                    print print_format % (w, freq[w], old_can_word, freq[old_can_word])
                    new_word_dict[w.lower()] = w
                continue

            # merge contain with the shortest one.
            word_size = len(w.split())
            contain_words = filter((lambda x: (word_size + 1 == len(x.split())) and w.lower() in x),
                                   new_word_dict.keys())

            _is_contain = False
            if contain_words:
                freq_curr = freq[w]
                for short_word in contain_words:
                    freq_short = freq[new_word_dict[short_word]]
                    merge_diff = math.fabs(freq_curr - freq_short) / min(freq_curr, freq_short)
                    if merge_diff <= new_word_merge_diff_threshold:
                        print contain_format % (w, freq[w], short_word, freq_short)
                        _is_contain = True
                        break

            if not _is_contain:
                new_word_dict[w.lower()] = w

        return new_word_dict.values()

    def _merge(self):
        # type list.
        words_by_freq = self._redis_conn.zrevrangebyscore(new_word_with_order, sys.maxint, new_word_min_freq, 0, -1,
                                                          True)
        words_by_ratio = self._redis_conn.zrevrangebyscore(ratio_new_word_with_order, sys.maxint, 5000, 0, -1, True)

        # type dict.
        self._dict_by_freq = {w[0]: w[1] for w in words_by_freq}
        self._dict_by_ratio = {w[0]: w[1] for w in words_by_ratio}
        words = set(self._dict_by_freq.keys()) & set(self._dict_by_ratio.keys())
        self._merge_words = self._merge_new_word(words, self._dict_by_freq)
        print len(words_by_freq), len(words_by_ratio), len(words), len(self._merge_words)

    def save_2_csv(self):
        if not self._output_dir:
            raise "Please input valid output_dir."

        if not self._merge_words:
            self._merge()

        file_name = 'result_' + datetime.datetime.now().strftime(time_format) + '.csv'
        file_path = os.path.join(self._output_dir, file_name)
        with open(file_path, "w+") as result:
            csv_write = csv.writer(result)
            for word in self._merge_words:
                freq = self._dict_by_freq[word]
                ratio = self._dict_by_ratio[word]
                csv_write.writerow([word, int(freq), ratio])

    def save_2_db(self):
        if not self._db_table:
            raise "Please check db's config"

        if not self._merge_words:
            self._merge()

        batch_insert_clause = 'INSERT INTO ' + self._db_table + ' (Keywords,Freq,Ratio,IsPhrase,added,updated) VALUES (%s, %s, %s,%s,%s,%s)'
        batch_update_clause = 'update ' + self._db_table + ' set Freq=%s,Ratio=%s,updated=%s where KeyWords=%s'
        query_model = 'select KeyWords,Freq,Status from ' + self._db_table + ' where KeyWords=\'%s\' order by added desc limit 1'
        try:
            # 通过获取到的数据库连接conn下的cursor()方法来创建游标。
            cur = self._db_conn.cursor()

            added = datetime.datetime.now().strftime(time_format_mysql)
            updated = added

            batch_insert_list = []
            batch_update_list = []

            for w in self._merge_words:
                current_freq = int(self._dict_by_freq[w])
                current_ratio = float(self._dict_by_ratio[w])
                query_clause = query_model % MySQLdb.escape_string(w)
                cur.execute(query_clause)
                res = cur.fetchone()
                if res:
                    remote_word, remote_freq, remote_status = res
                    if current_freq <= remote_freq:
                        continue
                    batch_update_list.append((current_freq, current_ratio, updated, w))
                else:
                    batch_insert_list.append((w, current_freq, current_ratio, 1, added, updated))

            print 'amount:', len(self._merge_words), 'update count:', len(batch_update_list), 'insert count:', len(
                batch_insert_list)

            while batch_insert_list:
                partial_list = batch_insert_list[:write_db_winow]
                print 'insert count:', cur.executemany(batch_insert_clause, partial_list)
                batch_insert_list = batch_insert_list[write_db_winow:]

                self._db_conn.commit()

            while batch_update_list:
                partial_list = batch_update_list[:write_db_winow]
                print 'update count:', cur.executemany(batch_update_clause, partial_list)
                batch_update_list = batch_update_list[write_db_winow:]

                self._db_conn.commit()
        except Exception as e:
            print('Error msg: ', e)
        finally:
            # 关闭游标
            cur.close()
            # 关闭数据库连接
            self._db_conn.close()
