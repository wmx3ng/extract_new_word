# -*- coding:utf-8 -*-
import csv
import datetime
import math
import os
import re
from functools import cmp_to_key

import pymysql as MySQLdb

from englory.new_word.cal_new_word.cal.input_tokens import InputTokens
from englory.new_word.cal_new_word.config.Config import *
from englory.new_word.cal_new_word.config.Config import time_format, time_format_mysql, write_db_winow
from englory.new_word.cal_new_word.data_clean.csv_2_item import CSV2Item

# match digital
digital_pattern = re.compile('(\d?|\d+)+\.?(\d?|\d+)')


class GenerateNewWords(object):
    def __init__(self, data_dirs, is_append, by_channel, channel_list=[]):
        self._data_dirs = data_dirs
        self._is_append = is_append
        self._by_channel = by_channel
        self._channel_list = channel_list

        self._merge_words = []

        self._dict_single_word = {}
        self._dict_group_word = {}
        self._dict_new_word_ratio = {}

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

    def _get_files_by_channel(self):
        files = []
        for data_dir in self._data_dirs:
            for (dirpath, dirnames, filenames) in os.walk(data_dir):
                files.extend([os.path.join(dirpath, file_name) for file_name in filenames])

        channel_dict = {}
        for file_name in files:
            prefix = file_name.split('.')[0]
            channel_tag = default_channel
            if self._by_channel:
                prefix_split = prefix.split('_')
                if len(prefix_split) > 1:
                    channel_tag = prefix_split[-1]

                if self._channel_list and channel_tag not in self._channel_list:
                    continue

            if channel_tag in channel_dict:
                channel_dict[channel_tag].append(file_name)
            else:
                channel_dict[channel_tag] = [file_name]

        return channel_dict

    def cal(self):
        dict_by_channel = self._get_files_by_channel()
        csv_2_item = CSV2Item()
        input_tokens = InputTokens()
        try:
            for channel_tag in dict_by_channel:
                print('handing channel_tag:', channel_tag)
                file_list = dict_by_channel[channel_tag]
                csv_2_item.set_file_list(file_list)
                article_list = csv_2_item.convert()
                if not article_list:
                    continue

                input_tokens.set_article_list(article_list)
                self._dict_single_word, self._dict_group_word, self._dict_new_word_ratio = input_tokens.resolve_text()

                self._merge()
                print('Updating group word 2 db...')
                self._save_by_group_word(channel_tag)

                if not self._by_channel:
                    print('Updating single word 2 db...')
                    self._save_by_single_word(channel_tag)

        except Exception as e:
            print(e)
        finally:
            self._close_db_conn()

    def _save_by_single_word(self, channel_tag):
        if not self._dict_single_word:
            return

        single_word_list = [k for k, f in self._dict_single_word.items() if
                            f > new_word_min_freq and not digital_pattern.fullmatch(k)]
        self._save_2_db(channel_tag, 0, single_word_list, self._dict_single_word)

    def _save_by_group_word(self, channel_tag):
        self._save_2_csv(channel_tag)
        self._save_2_db(channel_tag, 1, self._merge_words, self._dict_group_word)

    def _merge_new_word(self, words, freq):
        if not words or not freq:
            return []

        words_sort = sorted(words, key=cmp_to_key(lambda x, y: len(x) - len(y)), reverse=True)
        new_word_dict = {}
        for w in words_sort:
            # merge uppercase and lowercase. and select the bigger one by freq.
            if w.lower() in new_word_dict:
                old_can_word = new_word_dict[w.lower()]
                if freq[w] > freq[old_can_word]:
                    # print print_format % (w, freq[w], old_can_word, freq[old_can_word])
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
                        # print contain_format % (w, freq[w], short_word, freq_short)
                        _is_contain = True
                        break

            if not _is_contain:
                new_word_dict[w.lower()] = w

        return new_word_dict.values()

    def _merge(self):
        words = [k for k, v in self._dict_new_word_ratio.items()]
        self._merge_words = self._merge_new_word(words, self._dict_group_word)
        print('words_by_freq:', len(self._dict_group_word), 'words:', len(words), 'words_after_merge:',
              len(self._merge_words))

    def _save_2_csv(self, channel_tag):
        if not self._output_dir:
            raise "Please input valid output_dir."

        file_name = 'result_' + datetime.datetime.now().strftime(time_format) + '.csv'
        if channel_tag and channel_tag != default_channel:
            file_name = 'result_' + channel_tag + '_' + datetime.datetime.now().strftime(time_format) + '.csv'

        file_path = os.path.join(self._output_dir, file_name)
        with open(file_path, "w+") as result:
            csv_write = csv.writer(result)
            for word in self._merge_words:
                freq = self._dict_group_word[word]
                csv_write.writerow([word, int(freq)])

    def _close_db_conn(self):
        if self._db_conn:
            # 关闭数据库连接
            self._db_conn.close()

    def _save_2_db(self, channel_tag, is_phrase, word_list, word_freq_dict):
        if not self._db_table:
            raise "Please check db's config"

        batch_insert_clause = 'INSERT INTO ' + self._db_table + ' (Keywords,Freq,channel_tag,IsPhrase,added,updated) VALUES (%s,%s, %s,%s,%s,%s)'
        batch_update_clause = 'update ' + self._db_table + ' set Freq=%s,updated=%s where KeyWords=%s and channel_tag=%s'
        query_model = 'select KeyWords,Freq,Status from ' + self._db_table + ' where KeyWords=\'%s\' and channel_tag=\'%s\' order by added desc limit 1'

        # 通过获取到的数据库连接conn下的cursor()方法来创建游标。
        cur = self._db_conn.cursor()
        try:

            added = datetime.datetime.now().strftime(time_format_mysql)
            updated = added

            batch_insert_list = []
            batch_update_list = []

            for w in word_list:
                current_freq = int(word_freq_dict[w])
                query_clause = query_model % (MySQLdb.escape_string(w), channel_tag)
                cur.execute(query_clause)
                res = cur.fetchone()
                if res:
                    remote_word, remote_freq, remote_status = res
                    if not self._is_append and current_freq <= remote_freq:
                        continue

                    if not self._is_append:
                        batch_update_list.append((current_freq, updated, w, channel_tag))
                    else:
                        batch_update_list.append((current_freq + remote_freq, updated, w, channel_tag))
                else:
                    batch_insert_list.append((w, current_freq, channel_tag, is_phrase, added, updated))

            print('amount:', len(word_freq_dict), 'update count:', len(batch_update_list), 'insert count:',
                  len(batch_insert_list))

            while batch_insert_list:
                partial_list = batch_insert_list[:write_db_winow]
                print('insert count:', cur.executemany(batch_insert_clause, partial_list))
                batch_insert_list = batch_insert_list[write_db_winow:]

                self._db_conn.commit()

            while batch_update_list:
                partial_list = batch_update_list[:write_db_winow]
                print('update count:', cur.executemany(batch_update_clause, partial_list))
                batch_update_list = batch_update_list[write_db_winow:]

                self._db_conn.commit()
        except Exception as e:
            print('Error msg: ', e)
        finally:
            # 关闭游标
            cur.close()
