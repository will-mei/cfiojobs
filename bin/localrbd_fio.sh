#!/bin/bash

#fio -v || yum -y install fio || exit 1
mkdir -p $0-test
[[ $1 == "-p"  ]] && mode="&"

rbd_list=$(for i in {001..020};do echo rbd$i ;done)
pattern_list="read randread write randwrite"
bs_list="4k 256k 4m"

function wait_rbd_fio(){
    while ps aux |grep fio |grep rbdname= |grep -qv grep ;do
        sleep 30
    done
}

for BS in $bs_list ;do
    for PATTERN in $pattern_list ;do
        wait_rbd_fio
        for RBD in $rbd_list ;do
            eval  \
fio \
-numjobs=2 \
-iodepth=32 \
-rw=$PATTERN \
-ioengine=rbd \
-rbdname=$RBD \
-clientname=admin \
-pool=rbd \
-bs=$BS \
-direct=1 \
-size=100% \
-runtime=600 \
-ramp_time=30 \
-time_based \
-group_reporting \
--output-format=json  \
-name="2"-"$BS"-"$PATTERN"-"${RBD}".log.json \
&> "$0"-test/"$BS"-"$PATTERN"-"${RBD}".log.json $mode

        done
    done
done

#fio -iodepth=2 -rw=$ -ioengine=rbd -rbdname=rbd060 -clientname=admin -pool=rbd -bs=4k -size=200m -numjobs=1 -runtime=100 -group_reporting -name=2-  --output-format=json

