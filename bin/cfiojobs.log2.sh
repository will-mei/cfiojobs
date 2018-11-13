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

# analise json log build csv sheet report for single device
for i in $(ls $LOGDIR) ;do
    [[ -f "$LOGDIR/$i" ]] && continue
    [[ $i == "_report" ]] && continue
    if ls $LOGDIR/$i/*.log.json >/dev/null ;then 
        # err info os host logs 
        grep ^fio: $LOGDIR/$i/*.log.json >> $OUTPUTDIR/${LOGDIR##*/}"_fio-err.log"  
        sed -i "/^fio:/d" $LOGDIR/$i/*.log.json &>/dev/null 
        # rebuild csv report of disks
        rm -rf $LOGDIR/$i/*.csv 
        bash $(dirname $0)/cfiojobs.log.sh  $LOGDIR/$i &
        #cat $LOGDIR/$i/fio-err.log  > $OUTPUTDIR/${LOGDIR##*/}"_fio-err.log"
        #bash ./catcsv.sh $LOGDIR/$i/*.csv
    fi &
    if grep -q rbdname $LOGDIR/$i/*.log.json ;then 
        blk_type='rbd'
        echo "info: there will be no lateral contrast on rbd performance test."
    fi 
done && wait 

# clean old report 
[[ -n $(ls $OUTPUTDIR/{*.csv,*.tar,*.json} ) ]] && [[ ! -d $OUTPUTDIR/old_report ]] && mkdir -p $OUTPUTDIR/old_report
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

###############################
# auto excel 
function _host_excel_report(){
# generate excel format report for single host.
if python3 -V &>/dev/null ;then
    for  i in $(ls $LOGDIR) ;do
        python3 $(dirname $0)/cfiojobs.excel.py  $LOGDIR/$i
    done  || echo "python3 module pyexcel need to be installed"
else
    # show test report on stdout
    #for i in $(ls $LOGDIR) ;do
    #    bash ./catcsv.sh $LOGDIR/$i/*.csv
    #done
    # tips
    echo "$(_yellow "Warning"): python3 is not installed on host, the excel report will not be generated."
    # make excel report
    echo -e "\e[34m 1. after pyexcel(python3) installed,
            \r    to generate an excel report of the logs. you can use command:\n\e[0m
            \rfor i  in \$(ls $LOGDIR); do
            \r\tpython3 $(dirname $0)/cfiojobs.excel.py $LOGDIR/\$i
            \rdone\n"
    # catcsv.sh 
    echo -e "\e[34m 2. if no python3 enviroment on host,
            \r    to get a human readable preview of any csv sheet file in shell. you can use command:\n\e[0m
            \r ./catcsv.sh <filename.csv> \n"
fi
}
