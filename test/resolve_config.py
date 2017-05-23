# -*- coding:utf-8 -*-

import yaml


class ResolveConfig(object):
    def __init__(self, config_file):
        self.config_file = config_file
        with open(self.config_file) as config:
            self._yaml_config = yaml.load(config)

    def get_output_dir(self):
        return self._yaml_config.get('output_dir')

    def get_data_dir(self):
        return self._yaml_config.get('data_dir')

    def get_redis_config(self):
        return self._yaml_config.get('redis')

    def get_db_config(self):
        return self._yaml_config.get('db')
