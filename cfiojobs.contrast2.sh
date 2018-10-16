#!/bin/bash

source_report_dir=$1
source_report_name=${source_report_csv##*/}

reference_report_dir=$2
reference_report_name=${reference_report_dir##*/}

# usage
if [[ -z $2 ]] ;then
	echo "Usage: $0 <source_report_dir> <reference_report_dir>"
    exit 1
fi

# contrast
for i in $(ls "$source_report_dir/_report/$source_report_name"*_all_host.csv) ;do
	csv_name=${i##*/}
	# nvme or hdd
	if [[ ${csv_name//hdd/} != ${csv_name} ]] ;then
		type=hdd
	else
		type=nvme
	fi
	# check reference_report_json and contrast
	reference_report_json="$reference_report_dir/_report/$reference_report_name"_"$type".json
	if [[ -f $reference_report_json ]] ;then
        $(dirname $0)/cfiojobs.contrast.py $i $reference_report_json
	else
		echo "$reference_report_name missing or mismatch."
		echo "please check content in dir: $reference_report_dir/_report/ ."
        echo "you can try to rebuild json report with cmd: $(dirname $0)/cfiojobs.log2.sh $reference_report_dir"
		continue
	fi
done
