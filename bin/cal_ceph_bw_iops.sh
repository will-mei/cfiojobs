#!/bin/bash

WARM_TIME=50
TOTAL_TIME=$1
[[ -n "$1" ]] || exit 1
# 50(warm) + 5 interval * ( 5max +5min + 1 valid) = 105
[[ "$TOTAL_TIME" -gt $(($WARM_TIME + 5 * (5 + 5 + 1))) ]] || exit 1

sleep $WARM_TIME

bw_rd_tmpfile=$(mktemp)
bw_wr_tmpfile=$(mktemp)
iops_rd_tmpfile=$(mktemp)
iops_wr_tmpfile=$(mktemp)
tmp1=$(mktemp)


function cleanning(){
    rm -rf $bw_rd_tmpfile
    rm -rf $bw_wr_tmpfile
    rm -rf $iops_rd_tmpfile
    rm -rf $iops_wr_tmpfile
    rm -rf $tmp1
}
trap "cleanning; exit" 1 2 15

function conv_unit(){
# $1 value
# $2 unit
    value=$1
     unit=$2
    if   [[ $unit == "GB/s" ]]
    then
        out_put=$(echo $value |awk '{print$1 * 1000 * 1000}')
    elif [[ $unit == "MB/s" ]]
    then
        out_put=$(echo $value |awk '{print$1 * 1000}')
    elif [[ $unit == "kB/s" ]]
    then
        out_put=$value
    fi
    echo $out_put
}
function cal_avg(){
# $1 : file with one field of value each line
# files : tmp1
logfile=$1
    line_nu=$(cat $logfile |wc -l)
    line_l5=$[line_nu - 4]
    # first 5 (min) remove, last 5 (max) remove
    sort -n $logfile |sed -e "1,5"d -e "$line_l5,$"d >$tmp1
    # calculate avg value
    result=$(awk '{a+=$1}END{printf ("%.2f\n",a/NR)}' $tmp1)
    echo $result
}

count_time=$(( ($1 - 50) / 5 ))
while [[ $count_time -gt 0 ]] ;do
    # bw read
    bw_rd=$(ceph -s |grep client |awk -F[:,] '{print$2}')
    bw_rd=$(conv_unit $bw_rd)
    # bw write
    bw_wr=$(ceph -s |grep client |awk -F[:,] '{print$3}')
    bw_wr=$(conv_unit $bw_wr)
    # iops read
    iops_rd=$(ceph -s |grep client |awk -F[:,] '{print$4}' |awk '{print$1}')
    # iops write
    iops_wr=$(ceph -s |grep client |awk -F[:,] '{print$5}' |awk '{print$1}')
    echo "$bw_rd" >> $bw_rd_tmpfile
    echo "$bw_wr" >> $bw_wr_tmpfile
    echo "$iops_wr" >> $iops_rd_tmpfile
    echo "$iops_wr" >> $iops_wr_tmpfile
    count_time=$[count_time - 1]
    sleep 4
done

bw_rd_avg=$(cal_avg $bw_rd_tmpfile)
bw_wr_avg=$(cal_avg $bw_wr_tmpfile)
iops_rd_avg=$(cal_avg $iops_rd_tmpfile)
iops_wr_avg=$(cal_avg $iops_wr_tmpfile)

#output
echo "\
bw of read : $bw_rd_avg
bw of write : $bw_wr_avg
iops of read : $iops_rd_avg
iops of write : $iops_rd_avg"

cleanning
