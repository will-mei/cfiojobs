#!/bin/bash

if [[ -z $3 ]] || [[ ! -f $3 ]] ;then 
#if [[ -z $4 ]] || [[ ! -f $3 ]] ;then 
	echo "Usage: $0 <-p|-s>  < bs|'auto'>  [rbd_list_file] [outputdir]" 
	exit 0 
fi

fio -v &>/dev/null || yum -y install fio || exit 1

[[ $1 == "-p"  ]] && mode="&"
[[ $2 == 'auto' ]] && bs_list="4k 256k 4m" || bs_list="$2"
#[[ -f $3 ]] && rbd_list_file="$3" || exit 1
[[ -n $4 ]] && outputdir="$4" || outputdir="$0-test"

mkdir -p $outputdir 
pattern_list="read randread write randwrite"
#rbd_list=$(for i in {021..040};do echo rbd$i ;done)
numjobs=2
hostname=$HOSTNAME
blk_type='rbd'

function wait_rbd_fio(){
	#t=0
    while ps aux |grep fio |grep rbdname= |grep -qv grep ;do
	#if [[ $t -ge $(($runtime / 30 * 2)) ]];then
	#	kill -9 `ps aux |grep fio |grep rbdname= |awk '{print$2}'`
	#fi
	#local t=$[t +1]
        sleep 30
    done
}
for BS in $bs_list ;do 
    for PATTERN in ${pattern_list} ;do
        wait_rbd_fio
        while read RBD ;do
		eval \
fio \
-bs=$BS \
-size=100% \
-iodepth=4 \
-runtime=300 \
-rw=$PATTERN \
-ioengine=rbd \
-rbdname=$RBD \
-clientname=admin \
-pool=rbd \
-direct=1 \
-numjobs=$numjobs \
-ramp_time=30 \
-time_based \
-group_reporting \
--output-format=json  \
-name="$numjobs"-"$hostname"-"$blk_type"-"$BS"-"$PATTERN"-"${RBD}".log.json \
--output="$outputdir"/"$BS"-"$PATTERN"-"${RBD}".log.json &>>$outputdir/fio-err.log $mode
        done <$rbd_list_file
    done
done 
#fio -iodepth=2 -rw=$ -ioengine=rbd -rbdname=rbd060 -clientname=admin -pool=rbd -bs=4k -size=200m -numjobs=1 -runtime=100 -group_reporting -name=2-  --output-format=json
#fio -bs=4k -size=200m -rw=read -runtime=30 -ioengine=rbd -clientname=admin -pool=rbd -iodepth=2 -numjobs=1 -ramp_time=30 -direct=1 -time_based -group_reporting --output-format=json -rbdname=rbd060 -name=1-4k-read-rbd060.log.json
