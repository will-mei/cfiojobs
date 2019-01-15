#!/bin/bash

ceph_mon="172.18.211.54"
output_dir=$1
job_name=$2
job_batch_index=$3
ceph_log_name=${job_name}_ceph-df

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
# wait job end
#sleep $[runtime + 30]
_job_batch_check
ssh -n -q $ceph_mon 'ceph -f json-pretty df' >$output_dir/$ceph_log_name.after.json

