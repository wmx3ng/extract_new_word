# -*- coding: utf-8-*-
import csv
import re
import sys

csv.field_size_limit(sys.maxsize)

re_cdata = re.compile('//<!\[CDATA\[[^>]*//\]\]>', re.I)  # 匹配CDATA
re_script = re.compile('<\s*script[^>]*>[^<]*<\s*/\s*script\s*>', re.I)  # Script
re_style = re.compile('<\s*style[^>]*>[^<]*<\s*/\s*style\s*>', re.I)  # style
re_br = re.compile('<br\s*?/?>')  # 处理换行
re_h = re.compile('</?\w+[^>]*>')  # HTML标签
re_comment = re.compile('<!--[^>]*-->')  # HTML注释  ##过滤HTML中的标签  # 去掉多余的空行
blank_line = re.compile('\n+')  # 将HTML中标签等信息去掉

CHAR_ENTITIES = {'nbsp': ' ', '160': ' ',
                 'lt': '<', '60': '<',
                 'gt': '>', '62': '>',
                 'amp': '&', '38': '&',
                 'quot': '"', '34': '"', }

re_charEntity = re.compile(r'&#?(?P<name>\w+);')


# @param htmlstr HTML字符串.
def filter_tags(htmlstr):
    # 先过滤CDATA
    s = re_cdata.sub('', htmlstr)  # 去掉CDATA
    s = re_script.sub('', s)  # 去掉SCRIPT
    s = re_style.sub('', s)  # 去掉style
    s = re_br.sub('\n', s)  # 将br转换为换行
    s = re_h.sub('', s)  # 去掉HTML 标签
    s = re_comment.sub('', s)  # 去掉HTML注释
    s = blank_line.sub('\n', s)
    s = replaceCharEntity(s)  # 替换实体

    return s


##替换常用HTML字符实体.
# 使用正常的字符替换HTML中特殊的字符实体.
# 你可以添加新的实体字符到CHAR_ENTITIES中,处理更多HTML字符实体.
# @param htmlstr HTML字符串.
def replaceCharEntity(htmlstr):
    sz = re_charEntity.search(htmlstr)

    while sz:
        entity = sz.group()  # entity全称，如&gt;
        key = sz.group('name')  # 去除&;后entity,如&gt;为gt
        try:
            htmlstr = re_charEntity.sub(CHAR_ENTITIES[key], htmlstr, 1)
            # print (htmlstr)
            sz = re_charEntity.search(htmlstr)
        except KeyError:
            # 以空串代替
            htmlstr = re_charEntity.sub('', htmlstr, 1)
            sz = re_charEntity.search(htmlstr)
    return htmlstr


def repalce(s, re_exp, repl_string):
    return re_exp.sub(repl_string, s)


if __name__ == '__main__':
    with open('/home/wong/Documents/newscsv.csv', 'rb') as csvfile, open('target_news_2017-05-19', 'w+')as t:
        spamreader = csv.reader(csvfile, delimiter=',')
        spamreader = csv.reader((line.replace('\0', '').replace('\n', ' ').strip() for line in csvfile), delimiter=',')
        for row in spamreader:
            pure = filter_tags(row[2])
            t.write(pure)
