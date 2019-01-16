#!/bin/bash

lock_file=$0.running
[[ -f $lock_file ]] && exit 0 || touch $lock_file 
trap "rm -rf $lock_file" 1 2 15

# waiting end of test
echo "wait test $(date)"
while  ps aux |grep $(whoami) |grep cfiojobs |grep '\-\-'fio'\ ' |grep -v grep |grep -q $output_dir ;do
    sleep 5
done
echo "test end $(date)"

# join inut and output files names
output_dir=$1
source_csv=$output_dir/rados_df.csv
target_csv_list=$(ls $output_dir/_report/*_avg.csv)

echo "
output_dir: $output_dir
source_csv: $source_csv
target_list: $target_csv_list"

# update function 
function _update_csv(){
    # update title
    sed -i "1 s/$/\,ceph_bw\(MiB\/s\)\,ceph_iops/g" $avg_report_csv
    while read LINE ;do
        bp=${LINE%%,*}
        content=${LINE#*,}
        # attatch lines
        sed -i "/${bp}/s/$/&\,${content}/g" $avg_report_csv 
    done < $source_csv 
    echo "update $source_csv to $avg_report_csv done"
}

# update all avg worksheet csv 
for avg_report_csv in $target_csv_list ;do
    if [[ -f $source_csv ]] && [[ -f $avg_report_csv ]] ;then 
        _update_csv 
    else
        echo "$source_csv or $avg_report_csv file not found"
    fi
done

# remove lock 
rm -rf $lock_file # $source_csv 
