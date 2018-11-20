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
    for i in $(cat grouplist);do
        #[[ $(grep -vE "^$|^#" conf/$i'.blk' |sort -u |wc -l) -eq 1 ]] && continue
        ./cfiojobs.contrast2.sh $i"_parallel_"$timestamp $i"_single_"$timestamp
    done 
    tar czf test_"$timestamp"_report.tar.gz $(find ./ -type f -name *_all_host.csv) $(find ./ -type f -name *_all_host-contrast.csv)
    tar czf test_"$timestamp".tar.gz *"$timestamp" *"$timestamp".log 
fi
