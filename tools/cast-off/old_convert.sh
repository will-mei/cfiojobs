#!/bin/bash

[[ -z $1 ]] && echo "$0 cluster_log_dir1 d2 d3 ..." && exit 1
numjobs=2

#set pipe 
function _mk_pipe(){
    tmpfifo=$(mktemp -u)
    mkfifo $tmpfifo
    exec 100<>$tmpfifo
    rm -rf $tmpfifo
}
function _fill_pipe(){
    cpu_num=$(lscpu |grep ^'CPU(s):' |awk '{print$2}')
    proc_num=$(($cpu_num * $cpu_num))
    for ((n=1;n<=$proc_num;n++))
    do
        echo >&100
    done
}
function _close_pipe(){
    # close pipe
    exec 100>&-
    exec 100<&-
}
trap "_close_pipe;exit 0" 1 2 15

for j in $@;do
    log_list=$(find $j -type f -name *.log.json)
    for i in $log_list ;do 
        read -u 100
        {
            # add host name in background
            hostname=$(echo $i |cut -d'/' -f2 |awk -F'-' '{print$NF}')
            file_name=${i##*/}
            blk=$(echo $file |awk -F[-,.] '{a=NF-2;print$a}')
            [[ ${blk//nvme/} != $blk ]] && blk_type=nvme || blk_type=hdd 
            sed -i "s/[0-9].*log.json/${numjobs}-${hostname}-${blk_type}-oldtest.log.json/g" $i &
            # release pip
            echo >&100
        } &
    done
done
