#!/bin/bash
function single_test(){
for i in $(cat grouplist);do
    nohup ./cfiojobs -g $i -b $i -j allmode -f -s --fio -o $i"_"single"_"$(date +%Y%m%d) &> $i"_"single"_"$(date +%Y%m%d).log &
done
}

function wait_test(){
while ps aux |grep cfiojobs |grep '\-\-'fio |grep -vq grep ;do
    sleep 60
done
}

function parallel_test(){
for i in $(cat grouplist);do
    nohup ./cfiojobs -g $i -b $i -j allmode -f --fio -o $i"_"parallel"_"$(date +%Y%m%d) &> $i"_"parallel"_"$(date +%Y%m%d).log &
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
fi
