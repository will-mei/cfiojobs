#! /bin/bash

WARM_TIME=50
TOTAL_TIME=$1
[[ -n "$1" ]] || exit 1
[[ "$TOTAL_TIME" -ge 50 ]] || exit 1

: '
if [ $# -ne 3 ]; then
    echo "usage: ./calc_ceph.sh <warm_time> <total_time> <mode:r or w>"
    exit 0
fi
'

sleep $WARM_TIME

#if [ $MODE = "r" ] || [[ $MODE = "read" ]] || [[ $MODE = "randread" ]]; then

start_iops_read=`rados df | grep rbd | awk '{print $7}'`
start_bw_read=`rados df | grep rbd | awk '{print $8}'`
start_iops_write=`rados df | grep rbd | awk '{print $9}'`
start_bw_write=`rados df | grep rbd | awk '{print $10}'`
sleep $TOTAL_TIME
end_iops_read=`rados df | grep rbd | awk '{print $7}'`
end_bw_read=`rados df | grep rbd | awk '{print $8}'`
end_iops_write=`rados df | grep rbd | awk '{print $9}'`
end_bw_write=`rados df | grep rbd | awk '{print $10}'`

let avr_rd=($end_bw_read-$start_bw_read)/$TOTAL_TIME
let avr_iops=($end_iops_read-$start_iops_read)/$TOTAL_TIME
#echo "bw of read : $avr_rd kB/s"
echo "bw of read : $avr_rd kB/s"
echo "iops of read : $avr_iops"

#else
#sleep $TOTAL_TIME

let avr_wr=($end_bw_write-$start_bw_write)/$TOTAL_TIME
let avr_iops=($end_iops_write-$start_iops_write)/$TOTAL_TIME
echo "bw of write : $avr_wr kB/s"
echo "iops of write : $avr_iops"

#fi

