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
- redis服务器；
- mysql数据库；
- python2.7。

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
generate_new_word = GenerateNewWords(data_dirs, False, 'nlp', 11112, 1, ['2'])
generate_new_word.set_db_info('mysql-server', 3306, 'root', '', 'recommendation', 'thesaurus')
generate_new_word.set_output_dir('/home/wong/data/output')
generate_new_word.cal()
```

- 示例2：
```
# -*- coding:utf-8 -*-

from englory.new_word.cal_new_word.cal.generate_result import GenerateNewWords

data_dirs = ["/home/wong/data/news_list/20170521", "/home/wong/data/news_list/20170522"]
generate_new_word = GenerateNewWords(data_dirs, True, 'nlp', 11112, 1)
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
generate_new_word = GenerateNewWords(data_dirs, True, 'nlp', 11112, 1,channel_list)
generate_new_word.set_db_info('mysql-server', 3306, 'root', '', 'recommendation', 'thesaurus')
generate_new_word.set_output_dir('/home/wong/data/output')
generate_new_word.cal()
```

