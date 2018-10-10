#!/usr/bin/env python
# -*- coding:utf-8 -*-

from __future__ import print_function
import re
import os
import sys
import json
import time
import datetime
try:
    import pyexcel as p
except ImportError:
    print("\npyexcel is not installed or the env is not yet activated.\n")
    os.system('[[ -d vpy2 ]] && bash vpy2/bin/update_path_on_new_host.sh && echo -e "please run:\v\e[1;32m source vpy2/bin/activate\e[0m\n"')
    exit()
#finally:

try:
    json_logfile    = sys.argv[1]
except IndexError:
    print("this script requires a json format fio test log to run, please pass in the logfile name first.\n")
    exit()

# get value from json
with open(json_logfile,'r') as log_file:
    log_dict = json.load(log_file)
    fio_version = log_dict['fio version']
    _date       = time.strftime("%y%m%d",time.localtime(log_dict['timestamp']))
    if log_dict.has_key('disk_util'):
        pass
    else:
        print(json_logfile,': status abnormal, util value missing!')
        exit()
    _util       = log_dict['disk_util'][0]['util']
    _iodepth    = log_dict['global options']['iodepth']
    _rw         = log_dict['global options']['rw']
    _filename   = log_dict['global options']['filename'].replace('/','')
    print(p.get_sheet(adict = log_dict['global options']))
#    print(p.get_sheet(adict = log_dict['disk_util'][0]))

# bs - dic
def get_bs_dic(bs_str):
    #'2k/50:4k/20:256k/'
    _bs_dic   = dict()
    # each bs size, sep:':'
    for i in bs_str.split(':') :
        # name and value, sep:'/'
        _bs_dic[i.split('/')[0]] = i.split('/')[1]
    return _bs_dic

# calculate omit values in bs dict
def cal_omit(bs_dic):
    count = 0
    total = 0
    for key in bs_dic.keys() :
        var = bs_dic[key]
        if len(str(var)) == 0:
            count += 1
        # if not empty,sum values
        else :
            total += int(var)
    if total < 100 :
        value = (100 - total) / count
    else :
        value = 0
    # add value
    for i in bs_dic.keys() :
        if len(str(bs_dic[i])) == 0:
            bs_dic[i] = value
        else:
            bs_dic[i] = int(bs_dic[i])
    return bs_dic

def bs_str(a):
    b = str()
    for i in a.items():
        b += ' ' + str(i[0]) + '(' + str(i[1]) + '%)'
    return b

#util,pattern_percentage,bs_percentage,iodepth,bw,iops,latency_max,latency_avg
if _rw == "randrw":
    # pattern percentage
    if log_dict['global options'].has_key('rwmixread') :
        read_percentage  = log_dict['global options']['rwmixread']
        write_percentage = int(100 - float(read_percentage))
    else:
        read_percentage  = int(100 - float(log_dict['global options']['rwmixwrite']))
        write_percentage = log_dict['global options']['rwmixwrite']
    #print('read:',read_percentage,'write',write_percentage)
    pattern_percentage={'read':read_percentage,'write':write_percentage}
    # bs read + write, sep:','
    bs_split    = log_dict['global options']['bssplit'].split(',')
    #print('bs split list:', bs_split)
    bs_rd = cal_omit(get_bs_dic(bs_split[0]))
    #print('bs dict of read:',bs_rd)
    # in individual part of write bs set
    bs_rw = dict()
    if len(bs_split) > 1 :
        bs_dict = dict()
        for i in bs_split[1:]:
            #print('bs str of write:', i)
            bs_dict += get_bs_dic(i)
            #print('bs dict of write:', bs_dict)
            bs_rw += cal_omit(bs_dict)
    else:
        bs_rw = bs_rd
    #print('string of bs list:', bs_str(bs_rw))
    bs_percentage={'read':bs_rw,'write':bs_rw}
    title     = ['date','pattern_percentage(bs_percentage)','iodepth','bw(MiB/s)','iops','latency_max(ms)','latency_avg(ms)','util','fio_version']
#    print(title)
    for rw_mode in ["read","write"]:
        _pattern  = pattern_percentage[rw_mode]
        _bs       = bs_str(bs_percentage[rw_mode])
        _bw       = float(log_dict['jobs'][0][rw_mode]['bw']) / 1024
        _iops     = log_dict['jobs'][0][rw_mode]['iops']
        lat_max   = log_dict['jobs'][0][rw_mode]['lat_ns']['max'] /1000000
        lat_mean  = log_dict['jobs'][0][rw_mode]['lat_ns']['mean'] / 1000000
    # output
        sheet     = [title, [_date,rw_mode+'('+_pattern+'%:'+_bs+')',_iodepth,_bw,_iops,lat_max,lat_mean,_util,fio_version]]
        print(p.get_sheet(array=sheet))
else:
    _bs         = log_dict['global options']['bs']
    rw_mode     = _rw.split('rand')[-1:][0]
    #print(rw_mode,type(rw_mode))
    _bw         = float(log_dict['jobs'][0][rw_mode]['bw']) / 1024
    _iops       = log_dict['jobs'][0][rw_mode]['iops']
    lat_max     = log_dict['jobs'][0][rw_mode]['lat_ns']['max'] /1000000
    lat_mean    = log_dict['jobs'][0][rw_mode]['lat_ns']['mean'] / 1000000
    title       = ['date','bs_pattern','iodepth','bw(MiB/s)','iops','latency_max(ms)','latency_avg(ms)','util','fio_version']
    sheet=[title,[_date,_bs+_rw,_iodepth,_bw,_iops,lat_max,lat_mean,_util,fio_version]]
    print(p.get_sheet(array=sheet))
