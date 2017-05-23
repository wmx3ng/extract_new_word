# -*- coding:utf-8 -*-

import os

data_dir = '/home/wong/data'

f = []
for (dirpath, dirnames, filenames) in os.walk(data_dir):
    f.extend([os.path.join(dirpath, file_name) for file_name in filenames])

print f
