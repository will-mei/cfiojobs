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
        if len(line) < len(key_index_list):
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
def decimal2alphabet(i):
    n = int(i)
    #print('input:',i)
    alphabet_list = [chr(i) for i in range(97,123)]
    if n == 0 :
        return ''
    elif n % 26 == 0 :
        return alphabet_list[n -1]
    else:
        return (decimal2alphabet(int(n//26)) + alphabet_list[n%26 -1 ]).upper()

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

def list2csv_row(line, sep=','):
    return ''.join(map(lambda x: str(x) + sep , line ))

# save array of list  as csv
def save_csv(result, output_file):
    with open(output_file,'w') as csv_out :
        for i in result:
            line = ''.join(map(lambda x: str(x) + ',' , line ))
            csv_out.write(line)


#####################################################################################
# sort with fio pattern then data size
def pattern_sort(str_list):
#    print(str_list)
    result       = list()
    tmp_dic      = dict()
    pattern_list = ['read','write','trim','randread','randwrite','randtrim','randtrim','rw']
    # long name first 
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
            #certain_pattern_sub_list=tmp_dic[pattern]
            result += sorted(tmp_dic[pattern])
    return result

# sam bs size then sort by pattern 
def sam_unit_sort(str_list):
    result       = list()
    tmp_dic      = dict()
    key_list     = list()
    # [2,3,4,5,6]
    for s in str_list:
        n = re.findall("\d+",s)[0]
        if len(n) == 0 :
            continue
        elif n in key_list:
            continue
        else:
            key_list.append(n)
#    print(str_list,key_list)
    for s in str_list:
        n = re.findall("\d+",s)[0]
        # find same key group 
        for k in key_list: 
            if n == k:
                # add to group list in dict 
                if tmp_dic.has_key(k):
                    tmp_dic[k].append(s)
                else:
                    tmp_dic[k]=list()
                    tmp_dic[k].append(s)
                break
#    print(tmp_dic)
    for k in key_list:
        if tmp_dic.has_key(k):
            #certain_bs_sub_list = tmp_dic[k]
            result += pattern_sort(tmp_dic[k])
    return result

# a filter only return str with format bs+pattern
def pattern_filter(str_list):
    result    = list()
    tmp_dic   = dict()
    unit_list = ['b','k','m','g','p','e']
    for s in str_list:
        try :
            unit_name = ''.join(re.split(r'[^A-Za-z]', s))[0].lower()
        except:
            continue 
        for unit in unit_list:
            if unit_name == unit :
                if tmp_dic.has_key(unit):
                    tmp_dic[unit].append(s)
                else:
                    tmp_dic[unit] = list()
                    tmp_dic[unit].append(s)
    for unit in unit_list:
        if tmp_dic.has_key(unit):
            #certain_unit_sub_list = tmp_dic[unit]
            result += sam_unit_sort(tmp_dic[unit])
    return result

# sort string with data size unit
def block_size_sort(str_list):
    result    = list()
    tmp_dic   = dict()
    unit_list = ['b','k','m','g','p','e']
    # if not a pattern name recived
    tmp_dic['other'] = list()
    #print(str_list)
    for s in str_list:
        # '128krandread'
        try :
            unit_name = ''.join(re.split(r'[^A-Za-z]', s))[0].lower()
        except:
            tmp_dic['other'].append(s)
            continue 
        # say unit 'k'
        if unit_name in unit_list:
            pass
        else:
            tmp_dic['other'].append(s)
            continue 
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
            result += sam_unit_sort(tmp_dic[unit])
    result += sorted(tmp_dic['other'],key=lambda x : x.lower())
    return result
#####################################################################################

if __name__ == '__main__':
    print('sort and filter functions')
