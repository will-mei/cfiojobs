#!/bin/bash

if [[ -z $1 ]] ;then
    echo "Usage: $0  <-s|-p|-all>" && exit 1
fi
timestamp=$(date +%Y%m%d)
function single_test(){
for i in $(cat grouplist);do
    nohup ./cfiojobs -g $i -b $i -j allmode -f -s --fio -o $i"_"single"_"$timestamp &> $i"_"single"_"$timestamp.log &
done
}

function wait_test(){
while ps aux |grep cfiojobs |grep '\-\-'fio'\ ' |grep -vq grep ;do
    sleep 60
done
}

function parallel_test(){
for i in $(cat grouplist);do
    nohup ./cfiojobs -g $i -b $i -j allmode -f --fio -o $i"_"parallel"_"$timestamp &> $i"_"parallel"_"$timestamp.log &
done
}

if [[ $1 == "-s" ]] ;then
    single_test
elif [[ $1 == "-p" ]]
    parallel_test
elif [[ $1 == "-all" ]]
    single_test
    wait_test
    parallel_test
    wait_test
    ./cfiojobs.contrast2.sh $i"_"parallel"_"$timestamp $i"_"single"_"$timestamp
fi
