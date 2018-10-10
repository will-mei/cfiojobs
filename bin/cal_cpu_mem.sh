#!/bin/bash

total_time=$1

if [ -z "$total_time" ]; then
    echo "usage: ./calc_ceph.sh <total_caculate_time(second)> <h>(print some helpfull note in front)"
    exit 0
fi
#cpu usr and sys, (usr+sys)*core=total
cpu_usr_tmpfile=$(mktemp)
cpu_total_tmpfile=$(mktemp)
mem_tmpfile=$(mktemp)

echo "$$ usr_sys_cpu_tmp: $cpu_usr_tmpfile cpu_total_tmp: $cpu_total_tmpfile mem_tmp: $mem_tmpfile" >>cal_cpu_mem.sh.pid 
tcmu_runner_pid=$(ps aux |grep tcmu-runner|grep -v grep |awk '{print$2}')


#get usr and sys cpu usage record from top
top -b -d 1 -n $total_time -p $tcmu_runner_pid |grep Cpu >>$cpu_usr_tmpfile & 

#get cpu total usage
#top -b -d 1 -n $total_time -p $tcmu_runner_pid |grep $tcmu_runner_pid >>$cpu_total_tmpfile &

#use pid may grep get other lines, use process name instead
#top -b -d 1 -n $total_time -p $tcmu_runner_pid |grep "tcmu-runner" |grep $tcmu_runner_pid |sed '/Swap/d' >>$cpu_total_tmpfile &
#multy pipes gererate empty lines,the temp file get nothing, and awk report err when calculating a parametter form an empty line.

#not multy pipes,not sed, it's the process name!!!
#  1098 root      20   0   13.0g 570436 106992 S   0.0  3.5   1991:02 tcmu-runn+
#only tcmu-runn+ was showing out, use keyword "tcmu-runn" or "tcmu".
#top -b -d 1 -n $total_time -p $tcmu_runner_pid |grep $tcmu_runner_pid|grep "tcmu-run"  >>$cpu_total_tmpfile &

#set top running in a term columens with with a larger size, say more than 150 works better.
COLUMNS=150
top -b -d 1 -n $total_time -p $tcmu_runner_pid |grep $tcmu_runner_pid|grep "tcmu-runner"  >>$cpu_total_tmpfile &


#in consider of running for a ultra long time test, use file instead of pipe
#cpu_total_tmpfile1=$(mktemp) ;top -b -d 1 -n $total_time -p $tcmu_runner_pid >>$cpu_total_tmpfile1 & ;grep "tcmu-runner" $cpu_total_tmpfile1 >>$cpu_total_tmpfile &
#pipe is ok with long time running the pipe will be flushed, output data and keep its size.


#get mem usage record form top
top -b -d 1 -n $total_time -p $tcmu_runner_pid |grep buff |sed 's/+/\ /g' >>$mem_tmpfile &

#caclulate avg value
sleep $total_time

#cpu usr
#sed -e "1,5d" -e "\$"d $cpu_usr_tmpfile
cpu_usr_avg="$(awk '{a+=$2}END{printf ("%.2f\n",a/NR)}' $cpu_usr_tmpfile)"
#cpu sys
cpu_sys_avg=$(awk '{a+=$4}END{printf ("%.2f\n",a/NR)}' $cpu_usr_tmpfile)

#cpu total
#sed -e "1,5d" -e "\$"d  $cpu_total_tmpfile
#sed -i -e "1d" -e "/^KiB/d" -e "/Swap/d" -e "/^$/d" $cpu_total_tmpfile
#cat $cpu_total_tmpfile
cpu_total_avg="$(awk '{a+=$9}END{printf ("%.2f\n",a/NR)}' $cpu_total_tmpfile)"
echo $cpu_total_avg >cal_cpu_mem.sh.out

#mem used unit MB
mem_used_avg=`awk '{a+=$8}END{print a/NR/1024}' $mem_tmpfile`
#mem buffer unit MB
#mem_buff_avg=`awk '{a+=$10}END{print a/NR/1024"MB"}' $mem_tmpfile`
mem_buff_avg=`awk '{a+=$10}END{print a/NR/1024}' $mem_tmpfile`

if [ "$2" == "h" ]; then
echo "cpu_usr,cpu_sys,cpu_total,mem_used,mem_buffer"
fi

echo "$cpu_usr_avg,$cpu_sys_avg,$cpu_total_avg,$mem_used_avg,$mem_buff_avg"
rm -rf $cpu_usr_tmpfile
rm -rf $cpu_total_tmpfile
rm -rf $mem_tmpfile
sed -i "/$$/d" cal_cpu_mem.sh.pid 

