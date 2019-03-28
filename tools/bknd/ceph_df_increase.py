#!/usr/bin/env python
# coding=utf-8
import sys
import json
pool_name  = sys.argv[1]
log_before = sys.argv[2]
log_after  = sys.argv[3]

def get_used_kb(df_log):
    try:
        with open(df_log) as f:
            log_dict = json.load(f)
            #print int(log_dict['pools'][0]['stats']['kb_used'])
            pool_log = filter(lambda x : x['name'] == pool_name, log_dict['pools'] )
            return float(log_dict['pools'][0]['stats']['kb_used'])
    except:
        return 1

print( (get_used_kb(log_after)-get_used_kb(log_before)) / 2**10)
