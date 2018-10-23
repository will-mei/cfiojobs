#!/bin/bash

echo "$$" >>cal_tcmu_total_iops.sh.pid

if [[ -z "$1" ]] ;then
    echo "usag: bash $0 <time of seconds> "
    sed -i "/$$/d" cal_tcmu_total_iops.sh.pid
    exit 1
fi

#get io value before test form pminfo cmd
pminfo -V &>/dev/null || yum install pcp pcp-pmda-lio -y && systemctl enable pmcd && systemctl restart pmcd
start_write_value=`pminfo lio.summary -f |grep -A 1 lio.summary.total_write_mb |tail -1 |awk '{print $NF}'`
start_read_value=`pminfo lio.summary -f |grep -A 1 lio.summary.total_read_mb |tail -1 |awk '{print $NF}'`

#
sleep $1

end_write_value=`pminfo lio.summary -f |grep -A 1 lio.summary.total_write_mb |tail -1 |awk '{print $NF}'`
end_read_value=`pminfo lio.summary -f |grep -A 1 lio.summary.total_read_mb |tail -1 |awk '{print $NF}'`

echo "iops of write : `expr $end_write_value - $start_write_value`"
echo "iops of read : `expr $end_read_value - $start_read_value` "
sed -i "/$$/d" cal_tcmu_total_iops.sh.pid
