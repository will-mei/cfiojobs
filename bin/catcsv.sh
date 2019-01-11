#!/bin/bash
# double width characters will cause some output format problem

function _format_indent(){
    csv_file=$1
#(11 8 13 13 14 7 11 13 13 13 4 3)
WIDTH=($(awk '
BEGIN{
    FS=","
    zh="[^\x00-\xff]+"
}
function _zh_check(line){
    if(match(line, zh))
        zh_stat=0
    else
        zh_stat=1
}
function _zh_count(field){
    count1=0
    for(j=1;j<length(field);++j)
    {
        if(match(substr(field, j, 1), zh))
            count1=count1+1
        }
    count2=length(field)+count1
    if(wid[i]<count2)
        wid[i]=count2 
}
function _count(field){
    #
}
# initialize column width from begining.
{
    if(NR == 1)
        # init array
        for(i=1;i<=NF;i=i+1)
            wid[i]=length($i)
            col=NF
    }
# field width count loop
{
    _zh_check($0)
    # chinese characters in line
    if(_zh_stat == 0)
    {
        # count zh character acount
        for(i=1;i<=NF;i=i+1)
        {
            _zh_count($i)
            }
        }
    else
    {
        for(i=1;i<=NF;i=i+1)
            if(wid[i] < length($i))
                wid[i]=length($i)
        }
    if(col<NF)
        col=NF
    }
# output max values of column width and NF(col) 
END{
    for(i=1;i<=col;i=i+1)
        printf("%u ",wid[i])
    print col
    }' $csv_file ))
#echo ${WIDTH[*]}

#calculate column width
sep='+-'
# last one of the array is NF of the line, the offset will be -2 .
for i in $(seq 0 $((${#WIDTH[*]} -2))) ;do
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

awk -v "w=${WIDTH[*]}" -v "sep=$sep" "
BEGIN{
    FS=\",\"
    split(w,wid,\" \")
    print sep
    }
function _p_indent(i){
    #printf(\"%u/%s | \",i,wid[i])
    count1=0
    if( match(\$i, \"[^\x00-\xff]+\") )
        {
            for(j=1; j<=length(\$i); ++j)
            {
                if(match(substr(\$i, j, 1), \"[^\x00-\xff]\"))
                count1=count1+1
                #next
                }
        f=\"%-\"wid[i]-count1\"s | \"
        #printf(\"%u\",count1)
        }
    else
        f=\"%-\"wid[i]\"s | \"
    printf(f,\$i)
    }
{
    printf(\"%s\",\"| \")
}
{
    #for(i=1;i<=NF;i=i+1)
    for(i=1;i<=${WIDTH[-1]};i=i+1)
    _p_indent(i)
    if(i>NF)
        print\"\"
    }
{
    print sep
    }"  $csv_file 
# end of format indent 
}

#
for csv_file in $@ ;do
    [[ -f $csv_file ]] && _format_indent $csv_file || echo -e "\e[33m$csv_file \e[0m:\n csv file \"$csv_file\" not found!"
done
