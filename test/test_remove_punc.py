# -*- coding:utf-8 -*-
import re
import string

punc_pattern = re.compile('[' + string.punctuation + '\\s]+')
football_score = re.compile('\d+-\d+')
special_punc_pattern = re.compile('.*[' + """!"#%&()*+,:;<=>?@[\]^_`{|}~""" + ']+.*')
digital_pattern = re.compile('(\d?|\d+)+\.?(\d?|\d+)')


def _is_punc(word):
    if word is None:
        return True
    if punc_pattern.match(word):
        return True
    return False


# text = ['src=', 'co.', 'a_b', '=============', '     ', '.   ']
# for t in text:
#     print t, _is_punc(t)

# text = ['2a-2a', '=', '$5', 'www.baidu.com', 'https://www.baidu.com']
# for t in text:
#     print t
#     if special_punc_pattern.match(t):
#         print True
#     else:
#         print False
digits = ['2.6', '2.', '.3', '45.35343', '4', '4a', 'a4']
for d in digits:
    print(d)
    if digital_pattern.fullmatch(d):
        print('Y')
    else:
        print('N')
