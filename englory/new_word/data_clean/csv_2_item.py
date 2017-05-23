# -*- coding:utf-8 -*-
import csv
import os

from remove_html_tag import filter_tags


class CSV2Item(object):
    def __init__(self, data_dir, output_dir):
        self.data_dir = data_dir
        self.output_dir = output_dir

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

    def _get_file_list(self):
        files = []
        for (dirpath, dirnames, filenames) in os.walk(self.data_dir):
            files.extend([os.path.join(dirpath, file_name) for file_name in filenames])

        return files

    def convert(self):
        files = self._get_file_list()
        output_path = os.path.join(self.output_dir, 'news_tmp')
        output_path_with_sort = os.path.join(self.output_dir, 'news')
        print files, output_path
        with  open(output_path, 'w+')as t:
            csv_write = csv.writer(t)
            for input_path in files:
                print input_path
                with open(input_path, 'rb') as csvfile:
                    spam_reader = csv.reader((line.replace('\0', '').replace('\n', ' ').strip() for line in csvfile),
                                             delimiter=',')
                    for row in spam_reader:
                        pure = self._filter_by_len(filter_tags(row[3]))
                        if pure:
                            csv_write.writerow([pure])
        # sort and unique.
        cmd = 'sort ' + output_path + ' | uniq > ' + output_path_with_sort + ' ; rm ' + output_path
        os.system(cmd)


if __name__ == '__main__':
    csv_2_item = CSV2Item("/home/wong/data/news_list/20170522", "/home/wong/data/output")
    csv_2_item.convert()