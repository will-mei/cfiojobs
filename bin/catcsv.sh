#!/bin/bash
# output a human readable csv sheet.
if [[ -z $1 ]] ;then
    echo -e "usage: \v $0 <file1.csv file2.csv ... >\nmost UTF-8 encoded csv files are supported."
fi

function show_table(){
#calculate columns
col=$(awk -F',' '{print NF}' $csv_file |sort -nru |head -1)

function _p_width(){
[[ $# -gt 0 ]] && exec 0<$1

while read line
do
    local zh_part=${line//[a-zA-Z0-9[:punct:]]/}
    echo $(( ${#line} + ${#zh_part} )) ;
done<&0;
# close when no data
exec 0<&-
}

#calculate column width
sep='+-'
# array to save width of each column 
declare -a WIDTH

grep -q [^a-zA-Z0-9[:punct:]] $csv_file && has_doubl_width=1

for i in $(seq 1 $col);do
    # sort width max in column
    #WIDTH[$i]=$(awk -F','  "{l=length(\$$i);if(l<1)l=1;print l}" $csv_file|sort -nr |head -1)
    # chinese double width charactors
    #if grep -q [^a-zA-Z0-9[:punct:]] $csv_file ;then
    if [[ $has_doubl_width -eq 1 ]] ;then
        WIDTH[$i]=$(awk -F','  "{print\$$i}" $csv_file | _p_width |sort -nr |head -1)
    else
        #field with no chinese
        WIDTH[$i]=$(awk -F','  "{l=length(\$$i);if(l<1)l=1;print l}" $csv_file|sort -nr |head -1)
    fi
#calculate width of column
    tsep=""
    while [[ ${#tsep} -lt ${WIDTH[$i]} ]] ;do
        tsep+='-'
    done
    tsep+='-+-'
    sep+="$tsep"
done
sep=${sep:0:-1}
#echo $sep

# use a delimeter inplace of space, '-' inplace of empty field 
# print format table
echo -e "\e[33m$csv_file \e[0m:"
while read LINE ;do
    # deal space sequncial ','
    LINE=$(echo "$LINE" |sed -e "s/\ /TMPDELIMITEROFSPACE/g" \
                           -e "s/^\,/_\,/g" \
                           -e "s/\,\,/\,_\,/g" \
                           -e "s/\,\,/\,_\,/g")
    # calculate missing (field)columns number 
    f=$(echo ${LINE//,/ } |wc -w)
    # complete the short ones 
    while [[ $f -lt $col ]] ;do
        f=$[f + 1]
        LINE+=",_"
    done
    # start with a sep line 
    echo "$sep"
    #line start
    echo -n "| "
    f_nu=0
    # field completion
    for field in ${LINE//,/ };do
        # sep
        field="${field//TMPDELIMITEROFSPACE/ }"
        local space="${field//[^ ]/}"
        local l_space=${#space}
        # blank column 
        [[ "$field" == '_' ]] && field=' ' && fn="-1"
    #    echo -n "${field}"
        f_nu=$[f_nu + 1]
        zhpart=${field//[a-zA-Z0-9[:punct:]]/}
    #    wid_f=$(( ${#field} + ${#zhpart} )) 
        #wid_f=${#field}
        #printf "%-${WIDTH[$f_nu]}s" "${field}" 
        printf "%-$(( ${WIDTH[$f_nu]} + ${#zhpart} - ${l_space} $fn))b" "${field}" 
        fn=''
    #    while [[ $wid_f -lt ${WIDTH[$f_nu]} ]] ;do
    #        echo -en " "
    #        wid_f=$[wid_f + 1]
    #    done
        echo -n ' | '
    done
    echo ''
done < $csv_file
echo "$sep"
}

#
for csv_file in $@ ;do
    [[ -f $csv_file ]] && show_table || echo -e "\e[33m$csv_file \e[0m:\n csv file \"$csv_file\" not found!"
done
