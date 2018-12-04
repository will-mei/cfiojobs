#!/bin/bash
[[ -z $1 ]] && echo "Usage: $0 <cluster fio logdir>" && exit 1

function _yellow(){
    echo -e "\e[33m$@\e[0m"
}

#remove the last "/"
if [[ ${1:0-1:1} == / ]]
then
        LOGDIR="${1%/*}"
else
        LOGDIR="$1"
fi
# check logdir existence 
[[ ! -d $LOGDIR ]] && echo "dir $LOGDIR not exist!" &&  exit 1
# output dir 
OUTPUTDIR=$LOGDIR"/_report"
[[ -d $OUTPUTDIR ]] || mkdir -p $OUTPUTDIR
###############################################################
trap "_close_pipe;exit 0" 1 2 15

#set pipe 
mkfifo /tmp/tmpfifo
exec 100<>/tmp/tmpfifo
rm -rf /tmp/tmpfifo

function _close_pipe(){
	# close pipe
	exec 100>&-
	exec 100<&-
}

#for ((n=1;n<=100;n++))
#for ((n=1;n<=30;n++))
cpu_num=$(lscpu |grep ^'CPU(s):' |awk '{print$2}')
proc_num=$(($cpu_num * 10))
for ((n=1;n<=$proc_num;n++))
do
	echo >&100
done
###############################################################

# analise json log build csv sheet report for single device
for i in $(ls $LOGDIR) ;do
    read -u 100
    {
        if [[ -f "$LOGDIR/$i" ]] || [[ $i == "_report" ]] ;then
            :
        elif ls $LOGDIR/$i/*.log.json &>/dev/null ;then 
            # err info os host logs 
            grep ^fio: $LOGDIR/$i/*.log.json >> $OUTPUTDIR/${LOGDIR##*/}"_fio-err.log"  
            sed -i "/^fio:/d" $LOGDIR/$i/*.log.json &>/dev/null 
            # rebuild csv report of disks
            rm -rf $LOGDIR/$i/*.csv 
            bash $(dirname $0)/cfiojobs.dev.sh  $LOGDIR/$i &
            #cat $LOGDIR/$i/fio-err.log  > $OUTPUTDIR/${LOGDIR##*/}"_fio-err.log"
            #bash ./catcsv.sh $LOGDIR/$i/*.csv
        fi 
        echo >&100
    }&
    if [[ -f "$LOGDIR/$i" ]] || [[ $i == "_report" ]] ;then
        :
    elif grep -q rbdname $LOGDIR/$i/*.log.json 2>/dev/null ;then 
        blk_type='rbd'
        echo "info: there will be no lateral contrast on $LOGDIR/$i rbd performance test."
    fi 
done && wait 

# clean old report 
[[ -n $(ls $OUTPUTDIR/{*.csv,*.tar,*.json} 2>/dev/null ) ]] && [[ ! -d $OUTPUTDIR/old_report ]] && mkdir -p $OUTPUTDIR/old_report
mv $OUTPUTDIR/*.csv $OUTPUTDIR/*.tar $OUTPUTDIR/*.json $OUTPUTDIR/old_report/ &>/dev/null  

# make a report of the whole test.
if python2 $(dirname $0)/cfiojobs.log.py $LOGDIR $blk_type ;then
    # remove empty csv
    for i in $(ls "${LOGDIR##*/}"*.csv) ;do
        [[ $(wc -l < $i) -le 1 ]] && rm -rf $i
    done
    #tar -cf $OUTPUTDIR/"$LOGDIR"_peak_value.csv.tar "$LOGDIR"_hdd*.csv "$LOGDIR"_nvme*.csv
    tar -cf $OUTPUTDIR/"${LOGDIR##*/}"_peak_value.csv.tar "${LOGDIR##*/}"_*.csv
    mv "${LOGDIR##*/}"_*.csv $OUTPUTDIR/ &>/dev/null
    mv "${LOGDIR##*/}"_*.json $OUTPUTDIR/ &>/dev/null
else
    _yellow "build report from fio json logs in dir \"$LOGDIR\" failed!"
    exit 1
fi

