#!/bin/bash

ceph_mon="172.18.211.54"
pool_name="rbd"
output_dir=$1
job_name=$2
job_batch_index=$3
job_runtime=$4
ceph_log_name=${job_name}_ceph-df-increase 
output_file=$output_dir/ceph_df_increase.csv
[[ ${job_name//read/}  != $job_name ]] && col=7 || col=9

function _job_batch_check(){
    #check job_batch_index 
	recover_log=$output_dir/recover.log
    job_batch_info=$(sed -n 1p $recover_log)
    current_index=${job_batch_info##*,}
    # update job_batch_index and compare
    while [[ $current_index -eq $job_batch_index ]] ;do
        sleep 5 
        job_batch_info=$(sed -n 1p $recover_log)
        current_index=${job_batch_info##*,}
    done
}

    ssh -n -q $ceph_mon 'ceph -f json-pretty df' >$output_dir/$ceph_log_name.before.json
    iops_before=$(ssh -n -q $ceph_mon "rados df |grep $pool_name |awk \"{print\\\$$col}\"")

    # wait job end
    _job_batch_check

    ssh -n -q $ceph_mon 'ceph -f json-pretty df' >$output_dir/$ceph_log_name.after.json
    iops_after=$(ssh -n -q $ceph_mon "rados df |grep $pool_name |awk \"{print\\\$$col}\"")

    ###########################
    # only increased.
    ###########################
    bw_mb=$(python $(dirname $0)/ceph_df_increase.py $pool_name $output_dir/$ceph_log_name.before.json $output_dir/$ceph_log_name.before.json)
    iops=$[(iops_after - iops_before)/job_runtime]
    bw=$[bw/job_runtime]
    echo "${job_name/-/},$bw,$iops" >> $output_file

rm -rf $output_dir/${ceph_log_name}*.json
