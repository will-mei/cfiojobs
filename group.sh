#!/bin/bash

# default test settings
job_group=normal
#job_group=quicknormal
nvme_precondition="False"
timestamp=$(date +%Y%m%d)
output_excel_name="test_fio_"$timestamp'.xlsx'

# check host group and job group 
group_list=$(grep -vE "^$|^#" ./grouplist |sed ':label;N;s/\n/\ /;b label')
job_group_stat=$(grep -vE "^$|^#" ./cfiojobs.job |grep -q ^${job_group}; echo $?)

# help info 
if [[ -z $1 ]] || [[ -z $group_list ]];then
    [[ -z $group_list ]] && echo -e "\e[31mno valid host group name fond in grouplist!\e[0m\n"
    [[ $job_group_stat -ne 0 ]] && echo -e "\e[31mno job group name \"$job_group\" fond in grouplist!\e[0m\n"
    echo "function: auto test groups in grouplist."
    echo -e "\tdefault fio test job group: $job_group "
    echo -e "\tdefault nvme precondition : $nvme_precondition"
    echo -e "\tdefault excel report name : $output_excel_name"
    echo -e "\tcurrently valid group list: \"$group_list\""
    echo -e "Usage:\vnohup $0  <-s|-p|-all>  <output excel file name>  &>grouplist.log &"
    echo -e "Eg :  \vnohup $0  -all &>grouplist.log &"
    exit 1
fi
[[ -n $2 ]] && output_excel_name="$2"

function wait_test(){
    while ps aux |grep $(whoami) |grep cfiojobs |grep '\-\-'fio'\ ' |grep -vq grep ;do
        sleep 60
    done
}

function _nvme_precondition(){
        if grep -q nvme $(dirname $0)/conf/${i}.blk ;then 
            # precondition nvme disks 
            nohup $(dirname $0)/cfiojobs -g $i -fp "yum -y install nvme-cli " 
            nohup $(dirname $0)/cfiojobs -g $i -fp "for i in \$(lsblk -p |grep ^/ |grep nvme |awk '{print\$1}');do nvme format \$i ;done" 
            nohup $(dirname $0)/cfiojobs -g $i -b nvme -j fill1,fill2 -f --fio -o ${i}_data_fill &>${i}_data_fill.log &
            wait_test
        fi
}
function group_test(){
    mode=$1
    [[ $mode == "single" ]] && mode_arg="-s"
    for i in $group_list;do
        [[ $nvme_precondition == "True" ]]  && _nvme_precondition 
        nohup $(dirname $0)/cfiojobs -g $i -b $i -j $job_group -f $mode_arg --fio -o $i"_"$mode"_"$timestamp &> $i"_"$mode"_"$timestamp.log &
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
    for i in $group_list;do
        #[[ $(grep -vE "^$|^#" conf/$i'.blk' |sort -u |wc -l) -eq 1 ]] && continue
        $(dirname $0)/bin/cfiojobs.contrast2.sh $i"_parallel_"$timestamp $i"_single_"$timestamp $output_excel_name 
    done 
    tar czf test_"$timestamp"_report.tar.gz $(find ./ -type f -name *_all_host.csv) $(find ./ -type f -name *_all_host-contrast.csv) $output_excel_name
    tar czf test_"$timestamp".tar.gz *"$timestamp" *"$timestamp".log 
fi
