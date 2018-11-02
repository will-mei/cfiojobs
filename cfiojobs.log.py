#!/usr/bin/env python
# -*- coding:utf-8 -*-

from __future__ import print_function
import re
import os
import sys
import json
import time
import copy
import datetime

try:
    logdir    = sys.argv[1]
    #remove last '/'
    if logdir[-1] == '/' :
        logdir=logdir[:-1]
#    blk_type  = sys.argv[2]
    #nvme
#    peak_name = sys.argv[3]
except IndexError:
    print("this script requires: \n1. cluster fiolog dir, please pass in directory name first.")
    exit()
try:
    test_blk_type = sys.argv[2]
except IndexError:
    test_blk_type = 'normal'

host_list   = os.listdir(logdir)
# bs pattern - value - max/min/avg
max_info    = {'value':0.0,'hostname':'','filename':''}
min_info    = {'value':10**10,'hostname':'','filename':''}
peak_value  = {'max':copy.deepcopy(max_info),'min':copy.deepcopy(min_info),'sum':0.0,'sample':0}
key_index   = {'iodepth':0,'numjobs':0,'util':0,'size':0,'runtime':0,'bw':copy.deepcopy(peak_value),'iops':copy.deepcopy(peak_value),'latency_max':copy.deepcopy(peak_value),'latency_avg':copy.deepcopy(peak_value),'latency_min':copy.deepcopy(peak_value),'latency_stddev':copy.deepcopy(peak_value)}

# the performance threshold value
dev_weak_index  = {'hdd':0.9,'nvme':0.6,'rbd':0.6}
dev_name_index  = {'hdd':'dev','nvme':'nvme','rbd':'rbd'}

# calculate omit values in bs dict
def cal_omit_bs(bs_dic):
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
    # renew value
    for i in bs_dic.keys() :
        if len(str(bs_dic[i])) == 0:
            bs_dic[i] = value
        else:
            bs_dic[i] = int(bs_dic[i])
    return bs_dic

#bs dict - str
def bs_re2str(a):
    b = str()
    for i in a.items():
        b += ' ' + str(i[0]) + '(' + str(i[1]) + '%)'
    return b

# bs expr - dic
def bs_re2dict(bs_str):
    _bs_dic   = dict()
    for i in bs_str.split(':') :
        _bs_dic[i.split('/')[0]] = i.split('/')[1]
    return _bs_dic

# return a list of csv sheet of peak values (min|max|avg) in global dict
def peak_value_sheet(peak):
    #min
    result        = list()
    list_index    = ['iodepth','bw','iops','latency_max','latency_avg']
    title         = 'bs_pattern,iodepth,bw(MiB/s),iops,latency_max(ms),latency_avg(ms)'
    #print(title)
    result.append(title)
    for i in pattern_sort(sum_report.keys()) :
        #pattern
        line = str(i)
        title = 'bs_pattern'
        for j in list_index :
            #bw
            if   j == 'iodepth':
                line += ',' + str(sum_report[i][j])
            elif j != 'sum' or 'sample':
                if peak != 'avg':
                    line += ',' + str(sum_report[i][j][peak]['value']) + '(' + str(sum_report[i][j][peak]['hostname']) + ':' + str(sum_report[i][j][peak]['filename']) + ')'
                else:
                    v = sum_report[i][j]['sum'] / sum_report[i][j]['sample']
                    line += ',' + str(v) + '(sample:' + str(sum_report[i][j]['sample']) + ')' 
        result.append(line)
    return result

def update_value(pattern,p_index,p_value,p_hostname,p_filename):
    #print(pattern,sum_report.has_key(pattern))
    #print(sum_report.keys())
    #time.sleep(3)
    if sum_report.has_key(pattern):
        sum_report[pattern][p_index]['sum'] += float(p_value)
        sum_report[pattern][p_index]['sample'] += 1
        if   float(p_value) > float(sum_report[pattern][p_index]['max']['value']):
            sum_report[pattern][p_index]['max']['value'] = float(p_value)
            sum_report[pattern][p_index]['max']['hostname'] = p_hostname
            sum_report[pattern][p_index]['max']['filename'] = p_filename
        elif float(p_value) < float(sum_report[pattern][p_index]['min']['value']): 
            sum_report[pattern][p_index]['min']['value'] = float(p_value)
            sum_report[pattern][p_index]['min']['hostname'] = p_hostname
            sum_report[pattern][p_index]['min']['filename'] = p_filename
    else:
        sum_report[pattern] = copy.deepcopy(key_index)
        #max
        sum_report[pattern][p_index]['max']['value'] = float(p_value)
        sum_report[pattern][p_index]['max']['hostname'] = p_hostname
        sum_report[pattern][p_index]['max']['filename'] = p_filename
        #min
        sum_report[pattern][p_index]['min']['value'] = float(p_value)
        sum_report[pattern][p_index]['min']['hostname'] = p_hostname
        sum_report[pattern][p_index]['min']['filename'] = p_filename
        #avg
        sum_report[pattern][p_index]['sum'] = float(p_value)
        sum_report[pattern][p_index]['sample'] = 1

# sort string with data size unit
def byte_sort(str_list):
    result    = list()
    tmp_dic   = dict()
    unit_list = ['b','k','m','g','p','e']
    #print(str_list)
    for s in str_list:
        # '128krandread'
        unit_name = ''.join(re.split(r'[^A-Za-z]', s))[0].lower()
        # say unit 'k'
        for unit in unit_list:
            # b k m ...
            if unit_name == unit :
                # tmp_dic['k'] += '128krandread'
                if tmp_dic.has_key(unit):
                    tmp_dic[unit].append(s)
                else:
                    tmp_dic[unit] = list()
                    tmp_dic[unit].append(s)
                #print(tmp_dic)
    #print(tmp_dic)
    for unit in unit_list:
        # k m g ...
        if tmp_dic.has_key(unit):
            result += sorted(tmp_dic[unit],key=lambda x :int(re.findall("\d+",x)[0]) )
    return result

# sort with fio pattern then data size
def pattern_sort(str_list):
    #print(str_list)
    result       = list()
    tmp_dic      = dict()
    pattern_list = ['read','write','trim','randread','randwrite','randtrim','randtrim','rw']
    match_list   = sorted(pattern_list)
    for w in str_list :
        # 256krandwrite
        for pattern in match_list:
            #print('word:',w,'pattern:',pattern,'len:',len(pattern),'keyword:',w[0 - len(pattern):])
            if w[0 - len(pattern):] == pattern :
                if tmp_dic.has_key(pattern):
                    tmp_dic[pattern].append(w)
                else:
                    tmp_dic[pattern] = list()
                    tmp_dic[pattern].append(w)
                break
    for pattern in pattern_list:
        if tmp_dic.has_key(pattern):
            result += byte_sort(tmp_dic[pattern])
    return result

# get info from json and store to global dict
def store_to_global(log_dict,key_index):
    #key_index = [rw_mode,pattern_name,_hostname]
    # general info
    #fio_version = log_dict['fio version']
    _util       = log_dict['disk_util'][0]['util']
    _rw         = log_dict['global options']['rw']
    _size       = log_dict['global options']['size']
    _direct     = log_dict['global options']['direct']
    _runtime    = log_dict['global options']['runtime']
    _iodepth    = log_dict['global options']['iodepth']
    _ioengine   = log_dict['global options']['ioengine']
    try :
        _filename   = log_dict['global options']['filename']
    except KeyError:
        _filename   = log_dict['global options']['rbdname']
    _numjobs    = log_dict['jobs'][0]['job options']['name'].split('-')[0]
    #_date       = time.strftime("%y%m%d",time.localtime(log_dict['timestamp']))
    # get special index name
    rw_mode     = key_index[0]
    pattern_name= key_index[1]
    _hostname   = key_index[2]
    #
    _bw         = float(log_dict['jobs'][0][rw_mode]['bw']) / 1024
    _iops       = log_dict['jobs'][0][rw_mode]['iops']
    lat_max     = log_dict['jobs'][0][rw_mode]['lat_ns']['max'] /1000000
    lat_min     = log_dict['jobs'][0][rw_mode]['lat_ns']['min'] / 1000000
    lat_mean    = log_dict['jobs'][0][rw_mode]['lat_ns']['mean'] / 1000000
    lat_stddev  = log_dict['jobs'][0][rw_mode]['lat_ns']['stddev'] / 1000000
    # update values to global dict
    update_value(pattern_name,'bw',_bw,_hostname,_filename)
    update_value(pattern_name,'iops',_iops,_hostname,_filename)
    update_value(pattern_name,'latency_max',lat_max,_hostname,_filename)
    update_value(pattern_name,'latency_min',lat_min,_hostname,_filename)
    update_value(pattern_name,'latency_avg',lat_mean,_hostname,_filename)
    update_value(pattern_name,'latency_stddev',lat_stddev,_hostname,_filename)
    sum_report[pattern_name]['iodepth'] = _iodepth
    sum_report[pattern_name]['numjobs'] = _numjobs 
    sum_report[pattern_name]['runtime'] = _runtime 
    sum_report[pattern_name]['util']    = _util
    sum_report[pattern_name]['size']    = _size 
    # store log info to global perf list
    #omit_stat   = '○'
    omit_stat   = u'○'.encode('GB2312')
    perf_info = {'hostname':_hostname,'filename':_filename,'pattern_name':pattern_name,'iodepth':_iodepth,'bw':_bw,'iops':_iops,'stat':omit_stat,'lat_avg':lat_mean,'lat_max':lat_max,'lat_min':lat_min,'lat_stddev':lat_stddev,'util':_util,'size':_size,'runtime':_runtime,'direct':_direct,'numjobs':_numjobs,'ioengine':_ioengine}
    perf_list.append(perf_info)
        
# get value from json
def parse_json(fio_json_log):
    with open(fio_json_log,'r') as log_file:
        try:
            log_dict = json.load(log_file)
        except ValueError:
            print(fio_json_log,' : fail to load fio json log, skiped')
            return 0
        #print(log_dict)
        if log_dict.has_key('disk_util'):
            pass
        else:
            print(fio_json_log,': status abnormal, util value missing!')
            return 0
        # skip hdd or nvme drive
        try :
            blk_info = log_dict['global options']['filename'].split('/')[-1][0:4]
        except KeyError:
            blk_info = log_dict['global options']['rbdname']
        # nvme time , skip not nvme 
        if blk_type == 'nvme' and blk_info != blk_type:
            return 0
        # hdd/rbd time , skip nvme 
        elif blk_info == 'nvme':
            return 0
        #util,pattern_percentage,bs_percentage,iodepth,bw,iops,latency_max,latency_avg
        _util       = log_dict['disk_util'][0]['util']
        _rw         = log_dict['global options']['rw']
        _hostname   = host_name.split('-')[-1]
        # mixed read and write
        if _rw == "randrw":
            # pattern : percentage
            if log_dict['global options'].has_key('rwmixread') :
                read_percentage  = log_dict['global options']['rwmixread']
                write_percentage = int(100 - float(read_percentage))
            else:
                read_percentage  = int(100 - float(log_dict['global options']['rwmixwrite']))
                write_percentage = log_dict['global options']['rwmixwrite']
            pattern_percentage={'read':read_percentage,'write':write_percentage}
            # bssplit info, bs read + write, sep:','
            bs_split    = log_dict['global options']['bssplit'].split(',')
            # bs set of rw can be omited, only the first group is for read io.
            bs_rd = cal_omit_bs(bs_re2dict(bs_split[0]))
            bs_rw = dict()
            # 2k/50:256k/40:4m/,4k/50:8k/10,16k/ 
            # means : a workload that has 50% 2k reads, 40% 256k reads and 10% 4m reads, while having 50% 4k writes and 10% 8k writes and 16k for the rest 40%.
            if len(bs_split) > 1 :
                # individual and multy write bs set
                bs_dict = dict()
                for i in bs_split[1:]:
                    # get a dict of each bs
                    bs_dict += bs_re2dict(i)
                # calculate omitted bs values of bs dict
                bs_rw += cal_omit_bs(bs_dict)
            else:
                bs_rw = bs_rd
            #print('string of bs list:', bs_re2str(bs_rw))
            bs_percentage    = {'read':bs_rw,'write':bs_rw}
            # only two rw mode, store data of each mode
            for rw_mode in ["read","write"]:
                _bs          = bs_re2str(bs_percentage[rw_mode])
                _pattern     = pattern_percentage[rw_mode]
                pattern_name = str(_bs) + str(_rw)
                # log_dict +  [rw_mode,pattern_name,_hostname]
                key_index    = [rw_mode,pattern_name,_hostname]
                store_to_global(log_dict,key_index)
        else:
            _bs          = log_dict['global options']['bs']
            rw_mode      = _rw.split('rand')[-1:][0]
            pattern_name = str(_bs) + str(_rw)
            #store log value
            key_index    = [rw_mode,pattern_name,_hostname]
            store_to_global(log_dict,key_index)

def printf_perf_list(log_list,keys_of_log,csv_title,csv_name):
    # output weak host list to csv file
    with open(csv_name,'w') as f_csv :
        f_csv.write(csv_title)
        # add a empty sep line, record previous host name
        p_h  = str()
        for log in log_list :
            # one row a time
            line =str()
            # columns sorted by keys
            for key in keys_of_log :
                try :
                    field = str(log[key])
                except KeyError:
                    print('key missed:',log)
                    continue
                    field = 'x'
                if key == 'util':
                    field = field + '%'
                if len(line) == 0 :
                    line += field
                else:
                    line += ',' + field
            # empty or same as previous
            if p_h == '' :
                p_h = log['hostname']
            elif p_h == log['hostname'] :
                pass
            else:
#                print('previous:',p_h,'now:',log['hostname'])
                # new host, add a sep ,then add sep line
                f_csv.write('\n')
                # update hostname
                p_h = log['hostname']
            #end of line
            line += '\n'
            f_csv.write(line)

def compare_with_global(perf_list):
    # compare bw and iops value with global avg and give shortfall report
    for index_log in range(len(perf_list)):
        # 1 get log from list
        perf_log   = perf_list[index_log]
        #   bw and iops from this log
        v_bw       = float(perf_log['bw'])
        v_iops     = float(perf_log['iops'])
        #   bw and iops from global
        index_bw   = sum_report[perf_log['pattern_name']]['bw']
        index_iops = sum_report[perf_log['pattern_name']]['iops']
        index_lat  = sum_report[perf_log['pattern_name']]['latency_avg']
        #   calculate average value of bw and iops
        avg_bw     = index_bw['sum']   / index_bw['sample']
        avg_iops   = index_iops['sum'] / index_iops['sample']
        avg_lat    = index_lat['sum']  / index_lat['sample']
        # 2 avg info comparation
        perf_log['bw_global']     = str(avg_bw) 
        perf_log['iops_global']   = str(avg_iops) 
        perf_log['lat_avg_global'] = str(avg_lat)
        #   add deviation info to log
        perf_log['deviation']   = str(round(v_bw/avg_bw * 100 ,2) ) + '%' 
        if v_bw < avg_bw * weak_index :
            #perf_log['stat']   = u'●'.encode('GB2312')
            #perf_list[index_log]['stat']        = '●'
            perf_list[index_log]['stat']   = u'●'.encode('GB2312')
            perf_list[index_log]['bw_global']      = perf_log['bw_global']
            perf_list[index_log]['iops_global'] = perf_log['iops_global']
            perf_list[index_log]['lat_avg_global']  = perf_log['lat_avg_global']
            perf_list[index_log]['deviation']   = perf_log['deviation']
    #perf_list.sort(key=lambda x : int(x['hostname'].split('.')[3]) )
    perf_list.sort(key=lambda x : x['hostname'] )
    return perf_list 


for blk_type in ['hdd','nvme','rbd']:
    blk_log_stat= 1
    sum_report  = dict()
    # hostname,filename,pattern,index,value
    perf_list   = list()
    # different disk different standerd
    weak_index  = dev_weak_index[blk_type]
# analyse all json log in subdir
    for host_name in host_list :
        if host_name == '_report' :
            continue
        json_dir = os.path.join(logdir,host_name)
        if os.path.isdir(json_dir):
            for file_name in os.listdir(json_dir):
                if os.path.splitext(file_name)[1] == '.json' :
                    logfile = os.path.join(json_dir,file_name)
                    parse_json(logfile)
                    if dev_name_index[blk_type] in logfile:
                        blk_log_stat = 0
# if no nvme log then skip the rest.
    if blk_log_stat == 1:
        continue
# save result to json 
    json_output_file = './' + logdir.split('/')[-1] + '_' + blk_type + '.json' 
    json_data        = json.dumps(sum_report,indent=4)
    with open(json_output_file,'w') as sum_json:
        sum_json.write(json_data)
        sum_json.write('\n')
#peak_value_sheet('max')
    # output peak value report  to csv file
    for i in ['max','min','avg']:
        output_file = './' + logdir.split('/')[-1] + '_' + blk_type + '_' + i + '.csv'
        with open(output_file,'w') as f_peak:
            for line in peak_value_sheet(i):
                line = line + '\n'
                f_peak.write(line)
    # compare bw and iops value with global avg and give shortfall report
    perf_list = compare_with_global(perf_list)
    # set out put keys and title
    sheet_title = u'主机名,测试设备,块大小/模式,该盘测试带宽(MiB/s),测试带宽平均值(MiB/s),相对平均带宽的比值,"该盘带宽/同组所有磁盘带宽平均值筛选状态(低于90%标为●，否则记为○)",该测试每秒读写(iops),测试每秒读写(iops)平均值,该测试平均延迟(ms),测试延迟平均值(ms),该测试最大延迟(ms),该测试最低延迟(ms),读写队列深度,该测试作业并发进程数,该测试设备使用率,测试数据量,测试时长,读写数据引擎\n'.encode('GB2312')
    #sheet_title = u'主机名,测试设备,块大小/模式,该盘测试带宽(MiB/s),测试带宽平均值(MiB/s),相对平均带宽的比值,"该盘带宽/同组所有磁盘带宽平均值筛选状态(低于90%标为●，否则记为○)",该测试每秒读写(iops),测试每秒读写(iops)平均值,该测试平均延迟(ms),测试延迟平均值(ms),该测试最大延迟(ms),该测试最低延迟(ms),读写队列深度,该测试作业并发进程数,该测试设备使用率,测试数据量,测试时长,读写数据引擎\n'
    #sheet_title = '主机名,测试设备,块大小/模式,该盘测试带宽(MiB/s),测试带宽平均值(MiB/s),该测试带宽相对平均带宽的比值,同组筛选状态,该测试iops,测试iops平均值,该测试平均延迟(ms),测试延迟平均值(ms),该测试最大延迟(ms),该测试最低延迟(ms),读写队列深度,该测试作业并发进程数,该测试设备使用率,测试数据量,测试时长,读写数据引擎\n'
    #sheet_title = 'hostname,device,bs_pattern,bw(MiB/s),bw_global,deviation(%),stat,iops,iops_global,lat_avg(ms),lat_avg_global(ms),lat_max(ms),lat_min(ms),iodepth,numjobs,util,size,runtime,ioengine\n'
    #sheet_title  = 'hostname,filename,bs/pattern,bw(MiB/s),bw_global(MiB/s),deviation,stat,iops,iops_global,lat_avg(ms),lat_avg_global,lat_max,lat_min,iodepth,numjobs,util,size,runtime,ioengine\n'
    sheet_keys  = ['hostname','filename','pattern_name','bw','bw_global','deviation','stat','iops','iops_global','lat_avg','lat_avg_global','lat_max','lat_min','iodepth','numjobs','util','size','runtime','ioengine']
    if test_blk_type == 'rbd':
        sheet_title = u'主机名,测试设备,块大小/模式,该盘测试带宽(MiB/s),测试带宽平均值(MiB/s),该测试每秒读写(iops),测试每秒读写(iops)平均值,该测试平均延迟(ms),测试延迟平均值(ms),该测试最大延迟(ms),该测试最低延迟(ms),读写队列深度,该测试作业并发进程数,该测试设备使用率,测试数据量,测试时长,读写数据引擎\n'.encode('GB2312')
        sheet_keys  = ['hostname','filename','pattern_name','bw','bw_global','iops','iops_global','lat_avg','lat_avg_global','lat_max','lat_min','iodepth','numjobs','util','size','runtime','ioengine']
    elif test_blk_type == 'nocompare':
        sheet_title = u'主机名,测试设备,块大小/模式,测试带宽(MiB/s),每秒读写(iops),平均延迟(ms),最大延迟(ms),最低延迟(ms),iodepth,numjobs,util,size,runtime,ioengine\n'.encode('GB2312')
        sheet_keys  = ['hostname','filename','pattern_name','bw','iops','lat_avg','lat_max','lat_min','iodepth','numjobs','util','size','runtime','ioengine']
    # output all host list to csv file
    output_csv  = './' + logdir.split('/')[-1] + '_' + blk_type + '_all_host.csv'
    printf_perf_list(perf_list,sheet_keys,sheet_title,output_csv)

#print(byte_sort(sum_report.keys()))
#print(pattern_sort(sum_report.keys()))
