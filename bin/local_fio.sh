#!/bin/bash

fio -v || yum -y install fio || exit 1
mkdir -p $0-test
[[ $1 == "-p"  ]] && mode="&"

bs_list="4k 256k 4m"
pattern_list="read randread write randwrite"
blk_list=$(lsblk -ps |grep disk |grep -v "─" |awk '{print$1}')
for i in $blk_list ;do blk_seq+=","$i ;done

echo  "bs: ${bs_list// /,}" > "$0"-test/fio-batch.log
echo  "pattern: ${pattern_list// /,}" >> "$0"-test/fio-batch.log
echo  "blk: ${blk_seq//\//}" >> "$0"-test/fio-batch.log

for BS in $bs_list ;do
    for PATTERN in $pattern_list ;do
        for BLK in $blk_list ;do
            eval fio -bs=$BS -size=100% -rw=$PATTERN -runtime=600 -ramp_time=30 -iodepth=32 -numjobs=2 -direct=1 -ioengine=libaio -time_based -group_reporting --output-format=json -filename=$BLK -name="$BS"-"$PATTERN"-"${BLK//\//}".log.json &>"$0"-test/"$BS"-"$PATTERN"-"${BLK//\//}".log.json $mode
        done
    done
done
