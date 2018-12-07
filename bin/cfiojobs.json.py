#!/usr/bin/env python
# -*- coding:utf-8 -*-
import sys
import json
try:
    json_logfile    = sys.argv[1]
except IndexError:
    print("this script requires a json format fio test log to run, please pass in the logfile name first.")
    exit()
# get value from json
with open(json_logfile,'r') as log_file:
    try :
        log_dict = json.load(log_file)
    except ValueError:
        print('warning: ',json_logfile,'load failed, skiped!')
        sys.exit(1)
    if log_dict.has_key('disk_util'):
        pass
    else:
        print(json_logfile,': status abnormal, util value missing!')
        sys.exit(1)
