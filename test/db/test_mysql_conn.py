# -*- coding:utf-8 -*-

import pymysql as MySQLdb

db_conn = MySQLdb.connect(
    host='mysql-server',
    port=3306,
    user='root',
    passwd='',
    db='recommendation',
    charset='utf8'
)

window = 10000
query = 'select KeyWords,Freq,Status from ' + 'thesaurus limit %s,%s'
try:
    # 通过获取到的数据库连接conn下的cursor()方法来创建游标。
    cur = db_conn.cursor()
    page = 0
    while True:
        real_query = query % (page * window, window)
        page = page + 1
        print real_query
        cur.execute(real_query)
        res = cur.fetchone()
        print res
        word, freq, status = res
        print word
        if not res:
            break


except Exception as e:
    print('Error msg: ', e)
finally:
    # 关闭游标
    cur.close()
    # 关闭数据库连接
    db_conn.close()
