#!/bin/bash

lock_file=$0.running
[[ -f $lock_file ]] && exit 0 || touch $lock_file 
trap "rm -rf $lock_file" 1 2 15

# waiting end of test
while  ps aux |grep $(whoami) |grep cfiojobs |grep '\-\-'fio'\ ' |grep -v grep |grep -q $output_dir ;do
    sleep 5
done

# join inut and output files names
output_dir=$1
source_csv=$output_dir/rados_df.csv
target_csv_list=$(ls $output_dir/_report/*_avg.csv)

# update function 
function _update_csv(){
    # update title
    sed -i "1 s/$/\,ceph_bw(MiB/s)\,ceph_iops/g" $avg_report_csv
    while read LINE ;do
        bp=${LINE%%,*}
        content=${LINE#*,}
        # attatch lines
        sed -i "/${bp}/s/$/&\,${content}/g" $avg_report_csv 
    done < $source_csv 
}

# update all avg worksheet csv 
for avg_report_csv in $target_csv_list ;do
    if [[ -f $source_csv ]] && [[ -f $avg_report_csv ]] ;then 
        _update_ceph_df2csv 
    fi
done

# remove lock 
rm -rf $lock_file # $source_csv 
