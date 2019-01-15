#!/bin/bash

lock_file=$0.running
[[ -f $lock_file ]] && exit 0 || touch $lock_file 

output_dir=$1

# waiting end of test
while  ps aux |grep $(whoami) |grep cfiojobs |grep '\-\-'fio'\ ' |grep -v grep |grep -q $output_dir ;do
    sleep 10
done

ceph_df_csv=$output_dir/ceph_df.csv
avg_report_csv_list=$(ls $output_dir/_report/*_avg.csv)

function _update_ceph_df2csv(){
    # update title
    sed -i "1 s/$/\,ceph_bw\,ceph_iops/g" $avg_report_csv
    while read LINE ;do
        bp=${LINE%%,*}
        content=${LINE#*,}
        # attatch lines
        sed -i "/${bp}/s/$/&\,${content}/g" $avg_report_csv 
    done < $ceph_df_csv 
}

for avg_report_csv in $avg_report_csv_list;do
    if [[ -f $ceph_df_csv ]] && [[ -f $avg_report_csv ]] ;then 
        _update_ceph_df2csv 
    fi
done
