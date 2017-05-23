# -*- coding:utf-8 -*-
import datetime
import os
import sys
from resolve_config import ResolveConfig

time_format = "%Y%m%d"


def _get_date(key, arg_dict):
    if arg_dict[key]:
        return arg_dict[key]

    return datetime.datetime.now().strftime(time_format)


if __name__ == '__main__':
    """
    -Dconfig load config file.
    -Dstart  start date 2017-05-22
    -Dend    end date 2017-05-22
    -Dby_channel True or False
    -Dchannel list[]  channel ids.
    """
    arg = {v.split("=")[0]: v.split("=")[1] for v in sys.argv[1:]}
    if not arg['-Dconfig'] or not os.path.isfile(arg['-Dconfig']):
        raise "Please load config file."

    config_path = arg['-Dconfig']
    start_date = _get_date('-Dstart', arg)
    end_date = _get_date('-Dend', arg)

    resolve_config = ResolveConfig(config_path)

