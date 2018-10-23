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

nvme_ref_index  = 0.9
reference_index = 0.9
reference_title = "单盘独立测试"

# load json report form file as a reference data source.
with open(ref_json) as input_json:
    json_report = json.load(input_json)
    #print(json_report.keys())
    #print('\ninput csv:',source_csv,'\nreference json:',ref_json,'\noutput file:',output_file,'\n')

# a result list csv
result = list()
# a source list csv
source = list()

with open(source_csv,'r') as f:
    lines = f.readlines()
    for i in lines:
        source.append(i.split(','))

for i in range(len(source)) :
    row          = source[i]
    if i == 0 :
        #row.insert(7,  u'对照带宽(MiB/s)'.encode('GB2312'))
        #row.insert(8,  u'对照比值'.encode('GB2312'))
        #row.insert(9,  u'对照筛选状态'.encode('GB2312'))
        #row.insert(9,  u'是否合格(性能对比值不低于90%)'.encode('GB2312'))
        # 7+0
        row.insert(7,  u'单盘独立测试平均带宽(MiB/s)(同一时间同一主机上，只测试一块磁盘，最后计算得出所有磁盘的带宽平均值)'.encode('GB2312'))
        # 7+1
        row.insert(8,  u'满盘并发时该盘带宽/单盘独立测试时带宽平均值的百分比(%)'.encode('GB2312'))
        # 7+2
        row.insert(9,  u'满盘并发时该盘带宽/单盘独立测试时带宽平均值的筛选状态(低于90%标为●，否则记为○)'.encode('GB2312'))
        # 9+3
        row.insert(12, u'单盘独立测试的每秒读写(iops)平均值'.encode('GB2312'))
        # 11+4
        row.insert(15, u'单盘独立测试的平均延迟平均值(ms)'.encode('GB2312'))
        # 12+5
        row.insert(17, u'单盘独立测试的最大延迟平均值(ms)'.encode('GB2312'))
        # 13+6
        row.insert(19, u'单盘独立测试的最低延迟平均值(ms)'.encode('GB2312'))
        # 14+7
        row.insert(21, u'单盘独立测试的读写队列深度'.encode('GB2312'))
        # 15+8
        row.insert(23, u'单盘独立测试的作业并发进程数'.encode('GB2312'))
        # 16+9
        row.insert(25, u'单盘独立测试的设备使用率'.encode('GB2312'))
        # 17+10
        row.insert(27, u'单盘独立测试的测试数据量'.encode('GB2312'))
        # 18+11
        row.insert(29, u'单盘独立测试的测试时长'.encode('GB2312'))
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
        row.insert(17,stat)
        row.insert(19,stat)
        row.insert(21,stat)
        row.insert(23,stat)
        row.insert(25,stat)
        row.insert(27,stat)
        row.insert(29,stat)
        result.append(row)
        continue
    index_iops   = json_report[pattern_name]['iops']
    index_lat_avg= json_report[pattern_name]['latency_avg']
    index_lat_max= json_report[pattern_name]['latency_max']
    index_lat_min= json_report[pattern_name]['latency_min']
    avg_bw       = index_bw['sum']      / index_bw['sample']
    avg_iops     = index_iops['sum']    / index_iops['sample']
    avg_lat_avg  = index_lat_avg['sum'] / index_lat_avg['sample']
    avg_lat_max  = index_lat_max['sum'] / index_lat_max['sample']
    avg_lat_min  = index_lat_min['sum'] / index_lat_min['sample']
    #
    _iodepth     = json_report[pattern_name]['iodepth']
    _numjobs     = json_report[pattern_name]['numjobs']
    _util        = json_report[pattern_name]['util']
    _size        = json_report[pattern_name]['size']
    _runtime     = json_report[pattern_name]['runtime']
# calculate and compare
    ratio        = round(float(row[3]) / avg_bw * 100 ,2)
    str_ratio    = str(ratio) + '%'
# add to row
    row.insert(7,avg_bw)
    row.insert(8,str_ratio)
    # change index value when deal with nvme disks
    if row[1].split('/')[-1][0:4] == 'nvme'
        reference_index = nvme_ref_index
        #
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
    row.insert(15,avg_lat_avg)
    row.insert(17,avg_lat_max)
    row.insert(19,avg_lat_min)
    #
    row.insert(21,_iodepth)
    row.insert(23,_numjobs)
    row.insert(25,_util)
    row.insert(27,_size)
    row.insert(29,_runtime)
    #
    index_iops   = json_report[pattern_name]['iops']
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
