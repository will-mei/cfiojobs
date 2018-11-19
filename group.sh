#!/bin/bash

#job_group=quicknormal
job_group=allmode
if [[ -z $1 ]] ;then
    echo "test the group in grouplist single and/or parallel (default jobs: $job_group)."
    echo "Usage: nohup $0  <-s|-p|-all>  &>logfile.log" && exit 1
fi

timestamp=$(date +%Y%m%d)
function group_test(){
mode=$1
[[ $mode == "single" ]] && mode_arg="-s"
for i in $(cat grouplist);do
    nohup ./cfiojobs -g $i -b $i -j $job_group -f $mode_arg --fio -o $i"_"$mode"_"$timestamp &> $i"_"$mode"_"$timestamp.log &
done
}

function wait_test(){
while ps aux |grep $(whoami) |grep cfiojobs |grep '\-\-'fio'\ ' |grep -vq grep ;do
    sleep 60
done
}

if [[ $1 == "-s" ]] ;then
    group_test "single"
elif [[ $1 == "-p" ]] ;then
    group_test "parallel"
elif [[ $1 == "-all" ]] ;then
    group_test "parallel"
    wait_test
    group_test "single"
    wait_test
    ./cfiojobs.contrast2.sh $i"_"parallel"_"$timestamp $i"_"single"_"$timestamp
fi
