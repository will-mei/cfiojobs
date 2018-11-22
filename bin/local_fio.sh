#!/bin/bash

[[ -z $1 ]] && echo "\
    Usage: nohup  $0 <-p | -s>  &>xxx.log 
" && exit 1

fio -v 1>/dev/null || yum -y install fio
[[ $? -ne 0 ]] && exit 1

outputdir="$0-test"
mkdir -p $outputdir 
[[ $1 == "-p"  ]] && mode="&"

bs_list="4k 256k 4m"
pattern_list="read randread write randwrite"
blk_list=$(lsblk -ps |grep disk |grep -v ─ |awk '{print$1}')
numjobs=2

echo  "bs: ${bs_list// /,}" > "$outputdir"/fio-batch.log
echo  "pattern: ${pattern_list// /,}" >> "$outputdir"/fio-batch.log

for i in $blk_list ;do blk_seq+=","$i ;done
echo  "blk: ${blk_seq//\//}" >> "$outputdir"/fio-batch.log

function wait_fio(){
    #
    while ps aux |grep fio |grep -E "rbdname=|filename=" |grep -qv grep ;do
        sleep 30
    done
}

for BS in $bs_list ;do
    for PATTERN in $pattern_list ;do
        wait_fio 
        for BLK in $blk_list ;do
            eval fio -bs=$BS -size=100% -rw=$PATTERN -runtime=600 -ramp_time=30 -iodepth=32 -numjobs=$numjobs -direct=1 -ioengine=libaio -time_based -group_reporting --output-format=json -filename=$BLK -name="$numjobs"-"$BS"-"$PATTERN"-"${BLK//\//}".log.json &>"$outputdir"/"$BS"-"$PATTERN"-"${BLK//\//}".log.json $mode
        done
    done
done
