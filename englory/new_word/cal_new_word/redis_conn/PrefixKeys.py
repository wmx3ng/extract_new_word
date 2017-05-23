# -*- coding:utf-8 -*-

# store prefix
redis_prefix = "englory_"

# record meta info.
summary_meta = redis_prefix + 'summary_meta'
##词的总的数量
summary_meta_word_size = "word_size"
##单个词的数量
summary_meta_set_word_size = "set_word_size"

# 记录单个词的词频信息
single_word = redis_prefix + "single_word"

# 记录单个词的集合
set_single_word = redis_prefix + "set_single_word"

# 记录单个词的左、右连接词及其词频
adjoin_left_single_word = single_word + "_left_"
adjoin_right_single_word = single_word + "_right_"

# entropy of single word
left_entropy_single_word = single_word + "_left_entropy"
right_entropy_single_word = single_word + "_right_entropy"

# 记录新词的词频信息
new_word = redis_prefix + "new_word"
# 用zset记录新词，词频作为排序权重
new_word_with_order = redis_prefix + "new_word_with_order"

# ratio of new word
ratio_new_word_with_order = redis_prefix + "ratio_new_word"
entropy_new_word_with_order = redis_prefix + "entropy_new_word"
