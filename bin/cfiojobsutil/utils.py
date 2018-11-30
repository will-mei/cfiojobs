#!/usr/bin/env python
# coding=utf-8
import re 
import os 

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

def get_file_name(filename):
    (filepath,tmpfilename) = os.path.split(filename)
    (shortname,extension)  = os.path.splitext(tmpfilename)
    return filepath,shortname,extension

def print_dic(dic):
    #print('dict')
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

# load csv, remove title 
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
def save_csv(result, output_file):
    with open(output_file,'w') as csv_out :
        for i in result:
            line = ','.join(map(lambda x : str(x), line)) + '\n'
            csv_out.write(line)

def test_json_log():
    #
    pass 

def load_json_log():
    #
    pass 

def parse_rw():
    #
    pass 

def parse_bs():
    #
    pass


#####################################################################################

if __name__ == '__main__':
    print('sort and filter functions')
