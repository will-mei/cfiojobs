#!/usr/bin/env python
# -*- coding:utf-8 -*-

from __future__ import print_function
import os
import sys
import json

try:
    source_csv    = sys.argv[1]
    output_file   = os.path.splitext(source_csv)[0] + '-contrast.csv'
    ref_json      = sys.argv[2]
except IndexError:
    print("this script contrast fio csv report with json report, new report name: the_same_dir_as_inputfile/'xxx-contrast.csv'.\nand it requires: \n\t1. csv report name \n\t2. json report name\n please pass in these names first.")
    exit()

reference_index = 0.9

# load json report form file as a reference data source.
with open(ref_json) as input_json:
    json_report = json.load(input_json)
    #print(json_report.keys())
    #print('\ninput csv:',source_csv,'\nreference json:',ref_json,'\noutput file:',output_file,'\n')

result = list()

source = list()

with open(source_csv,'r') as f:
    lines = f.readlines()
    for i in lines:
        source.append(i.split(','))

for i in range(len(source)) :
    row          = source[i]
    if i == 0 :
        row.insert(7,  u'对照带宽(MiB/s)'.encode('GB2312'))
        row.insert(8,  u'对照比值'.encode('GB2312'))
        #row.insert(9,  u'对照筛选状态'.encode('GB2312'))
        row.insert(9,  u'是否合格(性能对比值不低于90%)'.encode('GB2312'))
        row.insert(12, u'对照测试的每秒读写(iops)平均值'.encode('GB2312'))
        row.insert(15, u'对照测试的延迟平均值(ms)'.encode('GB2312'))
        result.append(row)
        continue
# check pattern
    try :
        pattern_name = row[2]
    except IndexError:
        continue
# add ref value form json
    try :
        index_bw     = json_report[pattern_name]['bw']
    except KeyError:
        print('Warning:','%-10s' % pattern_name,'pattern info mismatch or missing')
        #stat     = 'Mismatch'
        #stat     = u'×'.encode('GB2312')
        stat     = u'…'.encode('GB2312')
        row.insert(7,stat)
        row.insert(8,stat)
        row.insert(9,stat)
        row.insert(12,stat)
        row.insert(15,stat)
        result.append(row)
        continue
    index_iops   = json_report[pattern_name]['iops']
    index_lat    = json_report[pattern_name]['latency_avg']
    avg_bw       = index_bw['sum']   / index_bw['sample']
    avg_iops     = index_iops['sum'] / index_iops['sample']
    avg_lat      = index_lat['sum']  / index_lat['sample']
# calculate and compare
    ratio        = round(float(row[3]) / avg_bw * 100 ,2)
    str_ratio    = str(ratio) + '%'
# add to row
    row.insert(7,avg_bw)
    row.insert(8,str_ratio)
    if   ratio >= reference_index * 100 :
        stat     = u'○'.encode('GB2312')
    elif ratio >= 75 :
        stat     = u'●'.encode('GB2312')
    else :
        #stat     = u'✖'.encode('GB2312')
        #stat     = u'✘'.encode('GB2312')
        stat     = u'●'.encode('GB2312')
    row.insert(9,stat)
    #
    row.insert(12,avg_iops)
    row.insert(15,avg_lat)
    result.append(row)
    
# save as csv
with open(output_file,'w') as csv_out :
    for i in result:
        line = str()
        for part_str in i :
            if len(line) == 0:
                line += str(part_str)
            else:
                line += ',' + str(part_str)
        csv_out.write(line)
#sheet_report.save_as(str(output_file))

