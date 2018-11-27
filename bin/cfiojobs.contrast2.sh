#!/bin/bash

# usage
if [[ -z $2 ]] ;then
	echo "Usage: $0 <parallel test log dir>  <single test log dir>  <output excel file name>"
    echo "the output excel file name can be omited"
    exit 1
fi
excel_name=$3

# remove '/' in the end of dir name 
[[ ${1:0-1:1} == "/" ]] && source_report_dir=${1%/*} || source_report_dir="$1"
# remove path
source_report_name=${source_report_dir##*/}

[[ ${2:0-1:1} == "/" ]] && reference_report_dir=${2%/*} || reference_report_dir="$2"
reference_report_name=${reference_report_dir##*/}

# contrast
for i in $(ls "$source_report_dir/_report/$source_report_name"*_all_host.csv) ;do
	csv_name=${i##*/}
	# nvme or hdd
	if [[ ${csv_name//hdd/} != ${csv_name} ]] ;then
		type=hdd
	elif [[ ${csv_name//nvme/} != ${csv_name} ]] ;then
		type=nvme
	else
        type=rbd
	fi
	# check reference_report_json and contrast
	#reference_report_json="$reference_report_dir/_report/$reference_report_name"_"$type".json
    reference_report=$(ls "$reference_report_dir/_report/$reference_report_name"*_all_host.csv |grep $type)
	if [[ -f $reference_report ]] ;then
        #$(dirname $0)/cfiojobs.contrast2.py $i $reference_report $type $excel_name 
        $(dirname $0)/cfiojobs.contrast2 $i $reference_report $type $excel_name 
	else
		echo "$reference_report_name missing or mismatch."
		echo "please check content in dir: $reference_report_dir/_report/ ."
        echo "you can try to rebuild json report with cmd: $(dirname $0)/cfiojobs.log.sh $reference_report_dir"
		continue
	fi
done
