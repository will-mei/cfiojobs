#!/bin/bash

ceph_mon="172.18.211.54"
pool_name="rbd"
output_dir=$1
job_name=$2
job_batch_index=$3
job_runtime=$4
rados_log_name=${job_name}_rados-df
output_file=$output_dir/rados_df.csv

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

    ###########################
    ssh -n -q $ceph_mon 'rados df --format=json-pretty ' >$output_dir/$rados_log_name.before.json

    # wait job end
    _job_batch_check

    ssh -n -q $ceph_mon 'rados df --format=json-pretty ' >$output_dir/$rados_log_name.after.json

    ###########################
    bw_iops="$(python $(dirname $0)/rados_df.py $pool_name $job_name $output_dir/$rados_log_name.before.json $output_dir/$rados_log_name.before.json)"

    ###########################
    echo "${job_name/-/},${bw_iops// /}" >> $output_file

# rm -rf $output_dir/${rados_log_name}*.json
