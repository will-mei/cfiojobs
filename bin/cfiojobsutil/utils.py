#!/usr/bin/env python
# coding=utf-8
from __future__ import print_function
import re 
import os 
import json
import time 

'csv , pattern_name functions and filters'

__author__ = 'william mei'

#####################################################################################

# store report to dict instead of list 
def array2dic(sheet_array, key_index_list):
    # key range set to field 1-3
    tmp_dic = dict()
    for line in sheet_array:
        if len(line) < max(key_index_list):
            continue 
        # key = ip + dev(filename) + bs_pattern
        tmp_list=list()
        for l in key_index_list:
            tmp_list += line[l] 
        k = ''.join(tmp_list)
        tmp_dic[k]=line 
    return tmp_dic 

#####################################################################################
# ./abc/def.h 
# ('./abc', 'def', '.h')
def get_file_name(filename):
    (filepath,tmpfilename) = os.path.split(filename)
    (shortname,extension)  = os.path.splitext(tmpfilename)
    return filepath,shortname,extension

# dict to text sheet 
def print_dic(dic):
    sep = '+'
    title =  content = '|'
    for i in dic:
        if len(str(i)) > len(str(dic[i])):
            sep     += '-' + '-' * (len(str(i)) +1) + '+'
            title   += ' ' + str(i) + ' |'
            content += ' ' + str(dic[i]) + ' '* (len(str(i)) - len(str(dic[i])) +1) + '|'
        else:
            sep     += '-' + '-'* (len(str(dic[i])) +1) + '+'
            title   += ' ' + str(i) + ' '* (len(str(dic[i])) - len(str(i)) +1) + '|'
            content += ' ' + str(dic[i]) + ' |'
    print('',sep,'\n',title,'\n',sep,'\n',content,'\n',sep,'\n')

# print a list of list with readable format 
def print_array(ll):
    #print('array')
    len_max_list=list()
    for i in ll:
        len_l = map(lambda x :len(str(x)) , i)
        if len(len_max_list) == 0:
            len_max_list = len_l
        else:
            len_max_list = map(lambda x, y : max([x,y]), len_max_list,len_l)
    sep = '+' + ''.join(map(lambda x : '-' + '-'*x + '-+', len_max_list ))
    print(sep)
    for i in ll:
        if len(i) < len(len_max_list):
            i += ['']* (len(len_max_list)-len(i))
        s = '|' + ''.join(map(lambda x, y : ' ' + str(y) + ' '*(x-len(str(y))) + ' |' ,len_max_list,i))
        print(s)
        print(sep)
        #

#####################################################################################
# decimal 2 alphabet 
def num2letter(i):
    n = int(i)
    #print('input:',i)
    alphabet_list = [chr(i) for i in range(97,123)]
    if n == 0 :
        return ''
    elif n % 26 == 0 :
        return alphabet_list[n -1]
    else:
        return (num2letter(int(n//26)) + alphabet_list[n%26 -1 ]).upper()

def ip2num(ip):
    if ip.replace('.','').isdigit():
        return int(''.join(map(lambda x : x.rjust(3, str(0)), ip.split('.') )) )
    else:
        return 300000000

# return a sorted ip list 
def ip_sort(ipl):
    return sorted(ipl, key = lambda x: ip2num(x) )

def ip_cmp(ip1, ip2):
    #sorted(ipl, cmp=ip_cmp )
    return ip2num(ip1) - ip2num(ip2)

# < 6
def unit2num(unit_name):
    unit_list = ['b','k','m','g','p','e']
    if unit_name.lower() in unit_list:
        return unit_list.index(unit_name.lower())
    else:
        return len(unit_list) + 1

# < 9
def pattern2num(pattern_name):
    pattern_list = ['read','write','trim','randread','randwrite','randtrim','randtrim','rw']
    if pattern_name in pattern_list:
        return pattern_list.index(pattern_name)
    else:
        return len(pattern_list) + 1

# 4krandwrite -> m 4 randwrite
# bs_size(num + unit) + pattern_name to number
def bp2num(bp, return_str=False, mark_fail=False):
    # validation stat 
    v = 0
    # unit , first letter
    try:
        bu  = ''.join(re.split(r'[^A-Za-z]', bp))[0].lower()
        bun = unit2num(bu)
    except:
        v = bun = 9
    # unit number , numbers 
    try :
        bsn = ''.join(re.split(r'[^0-9]', bp)).rjust(4, str(0))
    except:
        v, bsn = 9999, '9999'
    # pattern , letters from the 2nd to end 
    try :
        pt  = ''.join(re.split(r'[^A-Za-z]', bp))[1:].lower()
        ptn = pattern2num(pt)
    except:
        v = ptn = 9
    #print([str(bun), bsn, str(ptn)])
    if v != 0 and mark_fail == False:
        result = '999999'
    else:
        result = ''.join( [str(bun), bsn, str(ptn)] )
    if return_str == True:
        return result
    else:
        return int(result)

def bp_sort(bp_str_list, screening=False):
    if screening == False:
        return sorted(bp_str_list, key=lambda x : bp2num(x) )
    else:
        # sort - set - filter - str  
        return sorted(set([i for i in bp_str_list if bp2num(i, mark_fail=True) < 999999]), key=lambda x : bp2num(x))

# store report to dict instead of list 
def report_to_sortable_dic(sheet_array):
    # key range set to field 1-3
    tmp_dic = dict()
    for line in sheet_array:
        if len(line) < 3 :
            continue 
        # key = ip + dev(filename) + bs_pattern
        k  = str(ip2num(line[0]) )
        k += line[1] 
        k += bp2num(line[2], return_str=True)
        tmp_dic[k]=line 
    return tmp_dic 

# load csv ('GB2312'), sort certain column  
def load_csv(csv_file, sort_sheet=False, sort_column_index=0, reverse=True):
    with open(csv_file,'r') as f :
        sheet_csv  = list()
        unsortable = list()
        for line in f.readlines():
            # get line decoded and splited by coma
            try:
                line.decode('utf8')
                text_line = line.split(',')
            except:
                line.decode('GB2312')
                text_line = line.decode('GB2312').split(',')
            # check fields length 
            if len(text_line) < sort_column_index +1:
                for i in range(len(text_line) +1,sort_column_index +2):
                    text_line.append(None)
            # check field data type 
            for i in range(len(text_line) + 1):
                #int float 
                try:
                    text_line[i] = float(text_line[i])
                #text 
                except:
                    pass 
                    #continue 
            #print(text_line)
            sheet_csv.append(text_line)
    #return sheet_csv[1:] 
    if sort_sheet :
        return sorted(sheet_csv, key=lambda x: x[sort_column_index], reverse=reverse)
    else :
        return sheet_csv 

#def list2csv_row(line, sep=','):
#    return sep.join(line)

# save array of list  as csv
def save_csv(result_array, output_file, mode='w'):
    with open(output_file, mode) as result_csv :
        map(lambda line : result_csv.write( ','.join(map(lambda x : str(x), line)) + '\n'  ), result_array )

#####################################################################################
# get value from json
def load_json_log(fio_json_log):
    with open(fio_json_log,'r') as log_file:
        # load json 
        try:
            log_dict = json.load(log_file)
        except ValueError:
            print('warning:',fio_json_log,'load fio json log failed, skiped!')
            return {}
        # check util stat > 0 
        if log_dict.has_key('disk_util') and float(log_dict['disk_util'][0]['util']) > 0.0 :
            _util       = log_dict['disk_util'][0]['util']
        else:
            print('warning:',fio_json_log,'status abnormal, util value missing, skiped!')
            return {}
    return log_dict 

# check 
#1: hdd/rbd
#2: nvme
def confirm_disk_type(log_dict, blk_type):
    # get type info form log 
    try :
        blk_info = log_dict['global options']['filename'].split('/')[-1][0:4]
    except KeyError:
        blk_info = log_dict['global options']['rbdname']
    # nvme log, but want hdd/rbd 
    if blk_type == 'nvme' and blk_info != blk_type:
        return False
    # hdd/rbd log, but want nvme 
    elif blk_info == 'nvme':
        return False 
    else:
        return True
 
# transform str 2 a acertain int / 0
def s2int(s):
    if len(s) == 0:
        return 0
    else:
        try:
            return int(s)
        except:
            return 0

# 1: '4k/', 40
# 2: '4k/50, 40'
# 1: "'4k':40" 
# 2: "'4k':50"
def bsjust(bs_iterm, n):
    l = bs_iterm.split('/')
    if len(l[1]) > 0:
        return "'" + l[0] + "':" + l[1]
    else:
        return "'" + l[0] + "':" + str(n)

# bs expr - dic
# input : u'4k/50:256k/20:4m/30'
# dict output: {'256k': 40, '4m': 10, '4k': 50}
# str  output: '4m(10%) 256k(40%) 4k(50%)'
def parse_bs_expr(expr_str, dict_result=True ):
    # 1 remove empty space and split with ':'
    s = expr_str.replace(' ','').split(':')
    # ['4k/50', '8k/10', '4m/']
    num_all = len(s)
    # 2 calculate num of omited bs 
    num_omit = map(lambda x: len(x.split('/')[1]), s).count(0)
    if num_omit == 0 :
        result = eval('{' + ', '.join( map(lambda x: "'" + x.replace('/',"':"), s) ) + '}')
    else:
        # 3 calculate percentage of not omited 
        sum_omit = 100 - sum(map(lambda x : s2int(x.split('/')[1]), s))
        avg_left = sum_omit/num_omit
        result = eval('{' + ', '.join( map(lambda x: bsjust(x, avg_left), s) ) +'}')
    # result format 
    if dict_result == True :
        return result
    else:
        return ' '.join(map(lambda x: x[0] + '(' + str(x[1]) + '%)', result.items()))

# get mixed read and write rw mode from expr 
# bssplit info, bs read + bs write, sep:",", and bs set of rw can be omited, only the first group is for read io.
# input : 2k/50:256k/40:4m/,4k/50:8k/10,16k/  
# means : a workload that has 50% 2k reads, 40% 256k reads and 10% 4m reads, while having 50% 4k writes and 10% 8k writes and 16k for the rest 40%.
# output: ['read 70%: 256k(40%) 4m(10%) 4k(50%)', 'write 30%: 16k(40%) 8k(10%) 4k(50%)']
def parse_mixrw(log_dict):
    _rw         = log_dict['global options']['rw']
    # pattern : percentage
    if log_dict['global options'].has_key('rwmixread') :
        pct_r = log_dict['global options']['rwmixread']
        pct_w = str(100 - float(r_pct))
    else:
        pct_w = log_dict['global options']['rwmixwrite']
        pct_r = str(100 - float(log_dict['global options']['rwmixwrite']))
# pattern 
    pattern_percentage={'read':pct_r, 'write':pct_w}
    # parse read expr 
    bs_split    = log_dict['global options']['bssplit'].split(',')
    bs_r = parse_bs_expr(bs_split[0], dict_result=False)
    # str output : '4m(10%) 256k(40%) 4k(50%)'
    # check write expr if omited 
    if len(bs_split) > 1 :
        bs_w = parse_bs_expr(bs_split[1], dict_result=False)
    else:
        bs_w = bs_rd
# bs 
    bs_percentage    = {'read':bs_r, 'write':bs_w}
# pattern_name : bs + pattern = 'read 70%: 256k(40%) 4m(10%) 4k(50%)'
    # only two rw mode, store data of each mode
    bs_pattern_info = dict()
    for rw_mode in ['read', 'write']:
        _pattern_pct     = ' ' + pattern_percentage[rw_mode] + '%: '
        _bs_pct          = bs_percentage[rw_mode] 
        bs_pattern_info[rw_mode] = rw_mode + _pattern_pct + _bs_pct 
    return bs_pattern_info 

# get info from json and store to global dict
def flattern_log_dict(log_dict, rw_mode, with_private_name=True):
    # general info
    _version    = log_dict['fio version']
    _util       = log_dict['disk_util'][0]['util']
    #_rw         = log_dict['global options']['rw']
    _size       = log_dict['global options']['size']
    _direct     = log_dict['global options']['direct']
    try:
        _runtime    = log_dict['global options']['runtime']
    except:
        _runtime    = 'NA'
    _iodepth    = log_dict['global options']['iodepth']
    _ioengine   = log_dict['global options']['ioengine']
    try :
        _filename   = log_dict['global options']['filename']
    except KeyError:
        _filename   = log_dict['global options']['rbdname']
    # parse private options 
    if with_private_name:
        _job_name   = log_dict['jobs'][0]['job options']['name'].split('-')
        _numjobs    = _job_name[0]
        _host_name  = _job_name[1]
        _blk_type   = _job_name[2]
    # calculate
    _date       = time.strftime("%y%m%d",time.localtime(log_dict['timestamp']))
    _bw         = float(log_dict['jobs'][0][rw_mode]['bw']) / 1024
    _iops       = log_dict['jobs'][0][rw_mode]['iops']
    lat_max     = log_dict['jobs'][0][rw_mode]['lat_ns']['max'] /1000000
    lat_min     = log_dict['jobs'][0][rw_mode]['lat_ns']['min'] / 1000000
    lat_mean    = log_dict['jobs'][0][rw_mode]['lat_ns']['mean'] / 1000000
    lat_stddev  = log_dict['jobs'][0][rw_mode]['lat_ns']['stddev'] / 1000000
    #clat_ns_key= log_dict['jobs'][0]['rw_mode']['clat_ns']['percentile'].values()
    #clat_ms_seq_key =  map(lambda x: float(x), sorted(clat_ns_key))
    #[0.0, 1.0, 10.0, 20.0, 30.0, 40.0, 5.0, 50.0, 60.0, 70.0, 80.0, 90.0, 95.0, 99.0, 99.5, 99.9, 99.95, 99.99]
    clat_ns_seq = log_dict['jobs'][0][rw_mode]['clat_ns']['percentile'].values()
    clat_ms_seq = map(lambda x: float(x) /1000000, sorted(clat_ns_seq))
    #print(clat_ms_seq[0])
    if clat_ms_seq[0] == 0.0 :
        clat_ms_seq_str = ''.join(map(lambda x: ',' + str(x), clat_ms_seq[1:]))[1:]
    else:
        clat_ms_seq_str = ''.join(map(lambda x: ',' + str(x), clat_ms_seq))[1:]
    # store log info to result dict
    #omit_stat   = '○'
    #omit_stat   = u'○'.encode('GB2312')
    flattern_log_dict = {'version':_version,
                         'util':_util,
                         'size':_size,
                         'direct':_direct,
                         'runtime':_runtime,
                         'iodepth':_iodepth,
                         'ioengine':_ioengine,
                         'filename':_filename,
                         #'pattern_name':pattern_name,
                         'datetime':_date,
                         'bw':_bw,
                         'iops':_iops,
                         #'stat':omit_stat,
                         'lat_max':lat_max,
                         'lat_min':lat_min,
                         'lat_avg':lat_mean,
                         'lat_stddev':lat_stddev,
                         'clat_ms_seq_str':clat_ms_seq_str
                        }
    if with_private_name:
        flattern_log_dict['numjobs']  = _numjobs
        flattern_log_dict['hostname'] = _host_name
        flattern_log_dict['blk_type'] = _blk_type
    return flattern_log_dict  

# get performance info from fio log dict return a list of dict 
def parse_log_dict(log_dict):
    # read/randread/write/randwrite/randrw
    _rw         = log_dict['global options']['rw']
    # normal
    if _rw != "randrw":
        _bs          = log_dict['global options']['bs']
        # read / write 
        rw_mode      = _rw.split('rand')[-1:][0]
        # get a flattern_log_dict 
        perf_dict    = flattern_log_dict(log_dict, rw_mode)
        perf_dict['pattern_name'] = _bs + _rw
        return [ perf_dict ]
    #mixed
    else:
        result = list()
        bs_pattern_info = parse_mixrw(log_dict)
        for rw_mode in ['read', 'write']:
            perf_dict       = flattern_log_dict(log_dict, rw_mode)
            perf_dict['pattern_name'] = bs_pattern_info[rw_mode]
            result.append( perf_dict )
        return result 


#####################################################################################

if __name__ == '__main__':
    print('sort and filter functions')
