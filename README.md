**项目介绍**
-
加载大量文本文件，从中统计出高频词组，经过人工审核后，作为新词加入词库。

**程序支持功能**
-
- 支持从所有文本中统计；
- 支持按频道统计；
- 支持按指定频道统计。

**项目部署的系统需求**
-
- mysql数据库；
- python3。

**项目打包及部署方式**
-
- 在工程根目录执行 `python setup.py sdist`;
- 将dist目录下的打包文件拷贝至部署服务器，解压；
- 在解压根目录执行 `python setup.py install`即完成部署。

**项目运行示例脚本**
- 
- 示例1：
```
# -*- coding:utf-8 -*-

from englory.new_word.cal_new_word.cal.generate_result import GenerateNewWords

data_dirs = ["/home/wong/data/news_list/20170521", "/home/wong/data/news_list/20170522"]
generate_new_word = GenerateNewWords(data_dirs, False, False)
generate_new_word.set_db_info('mysql-server', 3306, 'root', '', 'recommendation', 'thesaurus')
generate_new_word.set_output_dir('/home/wong/data/output')
generate_new_word.cal()
```

- 示例2：
```
# -*- coding:utf-8 -*-

from englory.new_word.cal_new_word.cal.generate_result import GenerateNewWords

data_dirs = ["/home/wong/data/news_list/20170521", "/home/wong/data/news_list/20170522"]
generate_new_word = GenerateNewWords(data_dirs,False, True)
generate_new_word.set_db_info('mysql-server', 3306, 'root', '', 'recommendation', 'thesaurus')
generate_new_word.set_output_dir('/home/wong/data/output')
generate_new_word.cal()
```
- 示例3：
```
# -*- coding:utf-8 -*-

from englory.new_word.cal_new_word.cal.generate_result import GenerateNewWords

data_dirs = ["/home/wong/data/news_list/20170521", "/home/wong/data/news_list/20170522"]
channel_list=['2','3','5']
generate_new_word = GenerateNewWords(data_dirs,False, True,channel_list)
generate_new_word.set_db_info('mysql-server', 3306, 'root', '', 'recommendation', 'thesaurus')
generate_new_word.set_output_dir('/home/wong/data/output')
generate_new_word.cal()
```

**输入/输出格式**
- 
- 输入介绍
输入文本为csv格式文件，以“，”分隔（英文），取第4列。每行一条数据，单条数据示例：
```
2516544,2,"Selamat, Komo dan Brina Resmi Suami Istri","<p style=""text-align:center;""><img src=""https://image1.caping.co.id/news/20170520/52/2318264477A730A355.png_480A0A1A80.jpg""/></p><p><strong>POJOKSATU.id, JAKARTA</strong> &#8211; Kabar bahagia datang dari Komo Ricky.</p> <p>Host acara Katakan Putus ini resmi mempersunting kekasihnya, Brina, Sabtu (20/5/2017).</p> <p>Kabar ini diketahui lewat postingan foto akun lambe_lamis. Akun ini mengunggah empat foto terkait pernikahan Komo dengan tema serba putih.</p><center><p></p></center> <p>Salah satu foto yang diunggah terlihat Komo dan Brina memamerkan buku pernikahan mereka.</p> <p>Kabar bahagia dari Komo ini lantas direspon positif. Netizen memberikan ucapan dan doa untuk keduanya.</p> <p>&#8220;Congrats ya komoooo @komoricky,&#8221; kata akun cjmuchelly. &#8220;Selamat kak komo&#8230;mga langgeng,&#8221; ucap akun jenny_zera.</p> <p>&#8220;Resmi Jd adik ipar mas Indra Bekti dong ya mas komo nikah sma adik istrinya mas Indra (Adillajelita) saya ucapkan selamat ya mas komo dan istri semoga samarwa,&#8221; papar akun melliashilla.</p> <p><strong>(zul/pojoksatu)</strong></p> <h4></h4> </p>                <br><center></center>
```
- 数据库存储介绍
```
+-------------+--------------+------+-----+---------+----------------+
| Field       | Type         | Null | Key | Default | Extra          |
+-------------+--------------+------+-----+---------+----------------+
| Id          | int(11)      | NO   | PRI | NULL    | auto_increment |
| KeyWords    | varchar(255) | YES  | MUL | NULL    |                |
| Freq        | int(11)      | YES  |     | NULL    |                |
| Ratio       | double       | YES  |     | NULL    |                |
| Entropy     | double       | YES  |     | NULL    |                |
| Description | varchar(500) | YES  |     | NULL    |                |
| IsPhrase    | int(11)      | YES  |     | NULL    |                |
| Status      | tinyint(4)   | YES  |     | NULL    |                |
| added       | datetime     | YES  |     | NULL    |                |
| updated     | datetime     | YES  |     | NULL    |                |
| channel_tag | varchar(255) | YES  | MUL | NULL    |                |
+-------------+--------------+------+-----+---------+----------------+
```
1) KeyWords: 词组/高频词；
2) Freq: 词频；
3) IsPhrase: 0表示单个词，1表示词组；
4) Status: 1审核中的词，2有效词，3停用词;
5) added: 添加到数据的时间;
6) updated: 被更新的时间;
7) channel_tag: 词所属的频道，'0'表示所有数据，即不按频道分；其他值表示频道ID

**其他**
- 
- 频道ID获取

  频道ID的获取是由文本文件名称约定的，如`newslist_2.csv`即是表示'2'频道；
