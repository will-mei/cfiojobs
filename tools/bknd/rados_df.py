#!/usr/bin/env python
# coding=utf-8
import sys
import json
pool_name  = sys.argv[1]
runtime    = int(sys.argv[2])
log_before = sys.argv[3]
log_after  = sys.argv[4]

def get_used_kb(df_log):
    try:
        with open(df_log) as f:
            log_dict = json.load(f)
            if 'read' in df_log :
                ops_key   = 'read_ops'
                bytes_key = 'read_bytes'
            else:
                ops_key   = 'write_ops'
                bytes_key = 'write_bytes'
            pool_log = filter(lambda x : x['name'] == pool_name, log_dict['pools'] )
            return [int(pool_log[0][bytes_key]), int(pool_log[0][ops_key])]
    except:
        return [0, 0]

# values 
v_b = get_used_kb(log_before)
v_a = get_used_kb(log_after)
# delta 
d_bytes = v_a[0] - v_b[0]
d_ops = v_a[1] - v_b[1]
#print(v_b, v_a)

print (d_bytes/2**10 /runtime), ',', d_ops/runtime
