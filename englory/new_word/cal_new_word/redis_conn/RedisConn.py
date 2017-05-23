# -*- coding:utf-8 -*-
import redis


class RedisConn:
    def __init__(self):
        pass

    @staticmethod
    def redis_conn(host, port, db):
        return redis.Redis(host, port, db)
