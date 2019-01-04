#!/bin/bash

[[ -z $1 ]] && echo "$0 cluster_log_dir1 d2 d3 ..." && exit 1
numjobs=2

function _pipe_exec(){
    #
    [[ $# -gt 0  ]] && exec 0<$1
    while read line
    do
        # dir and file name 
        df=${line#*/}
        # file name 
        f=${line##*/}
        # dir name 
        d=${df%%/*}
        hostname=${d##*-}
        # job info
        i=${f%%.*}
        blk=${i##*-}
        # blk type 
        if [[ ${blk//nvme/} != $blk ]] ;then
            blk_type=nvme
        elif [[ ${blk//dev/} != $blk ]] ;then
            blk_type=hdd
        else
            blk_type=rbd
        fi
        sed -i "s/[0-9].*log.json/${numjobs}-${hostname}-${blk_type}-${i}.log.json/g" $line
        #echo "$line $hostname $blk_type $i" ;
    done<&0;
    # close when no data
    exec 0<&-
}

for j in $@;do
    find $j -type f -name *.log.json |_pipe_exec  
    python $(dirname $0)/../cfiojobs.log2.py $j
done
