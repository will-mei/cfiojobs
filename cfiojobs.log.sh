#!/bin/bash

LOGDIR="$1"
[[ -z $1 ]] && echo "Usage: $0  <host fio logdir>" && exit 1
#bs_list="$(awk -F'-' '{print$1}' $LOGDIR/fio-batch.log |sort -un)"
#pattern_list="$(awk -F'-' '{print$2}' $LOGDIR/fio-batch.log |sort -u)"
#blk_list="$(awk -F'-' '{print$3}' $LOGDIR/fio-batch.log |sort -u)"
bs_list="$(grep "^bs:" $LOGDIR/fio-batch.log |cut -d':' -f2 |sed 's/\,/\ /g' )"
pattern_list="$(grep "^pattern:" $LOGDIR/fio-batch.log |cut -d':' -f2 |sed 's/\,/\ /g' )"
blk_list="$(grep "^blk:" $LOGDIR/fio-batch.log |cut -d':' -f2 |sed 's/\,/\ /g' )"

#common
OUTPUT_DIR="$LOGDIR"
mkdir -p $OUTPUT_DIR
grep ^fio: $OUTPUT_DIR/*.json >> $OUTPUT_DIR/fio-err.log

json_script="$(dirname $0)/cfiojobs.json.py"


# analyse test logs
for BS in $bs_list 
do
    for PATTERN in $pattern_list
    do
#        echo -e "\e[33m host: $LOGDIR, bs: $BS, PATTERN:$PATTERN \e[0m"
        #tcmu/ceph iops/sys_load for each pattern
        bknd_tcmu_outputfile=$OUTPUT_DIR/fio-bknd-tcmu.csv
        bknd_ceph_outputfile=$OUTPUT_DIR/fio-bknd-ceph.csv

        #tcmu iops
        tcmu_iops_logfile=$LOGDIR/$BS-$PATTERN-tcmu_iops.log
        #tcmu sys load
        tcmu_load_logfile=$LOGDIR/$BS-$PATTERN-tcmu_load.log
        if [[ -f $tcmu_iops_logfile ]] && [[ -f $tcmu_load_logfile ]] ;then
            #take randread as read, randwrite as write
            keywords=${PATTERN#rand*}
            tcmu_iops=$(sed "/known hosts/"d $tcmu_iops_logfile \
                      |grep "iops of $keywords :" \
                      |awk '{print$5}')
            #echo "$tcmu_iops" >> $tcmu_iops_outputfile

            #get load info
            tcmu_host_load=$(sed "/known hosts/"d $tcmu_load_logfile \
                      |tail -1 \
                      |awk '{print$NF}')
            #echo "tcmu iops: $tcmu_iops, host load: $tcmu_host_load"
            #sleep 3
            [[ -f $bknd_tcmu_outputfile ]] || echo "bs_pattern,tcmu_iops,tcmu_load(cpu),,,tcmu_load(mem)," > $bknd_tcmu_outputfile
            echo "$BS$PATTERN,$tcmu_iops,$tcmu_host_load" >>$bknd_tcmu_outputfile
#        else
#            echo "warning: tcmu load and iops log analyse skiped."
        fi

        #ceph bw iops
        ceph_iobw_logfile=$LOGDIR/$BS-$PATTERN-ceph_iobw.log 
        if [[ -f $ceph_iobw_logfile ]] ;then
            #take randread as read, randwrite as write
            ceph_bw=$(sed "/known hosts/"d $ceph_iobw_logfile \
                    |grep "^bw of ${PATTERN#rand*} :" \
                    |awk '{print$5}')
            ceph_iops=$(sed "/known hosts/"d $ceph_iobw_logfile \
                      |grep "^iops of ${PATTERN#rand*} :" \
                      |awk '{print$5}')
            #echo "ceph bw: $ceph_bw, ceph iops: $ceph_iops"

            [[ -f $bknd_ceph_outputfile ]] || echo "bs_pattern,ceph_bw,ceph_iops" > $bknd_ceph_outputfile
            echo "$BS$PATTERN,$ceph_bw,$ceph_iops" >>$bknd_ceph_outputfile
#        else
#            echo "warning: ceph log analyse skiped."
        fi

        for BLK in $blk_list
        do
            #echo "BLK : $BLK"
            #output file
            fio_outputfile=$OUTPUT_DIR/fio-"$BLK".csv
            #source files
            fio_logfile=$LOGDIR/$BS-$PATTERN-$BLK".log.json"
            if [[ -f $fio_logfile ]] ;then
                :
            else
                #echo -e "\e[31m warning: $BS $PATTERN $BLK logfile $fio_logfile is missing, log analyse skiped! \e[0m"
                echo -e "warning: $fio_logfile is missing, skiped!"
                continue
            fi

            # fio_logfile
            #echo -e "\e[33m$fio_logfile\e[0m"

#            if [[ ${fio_logfile##*"."} != 'json' ]] ;then
#                [[ -f $fio_outputfile ]] || echo "bs_pattern,iodepth,bw(MiB/s),iops,latency_max(ms),latency_avg(ms)" > $fio_outputfile
#                echo "$BS$PATTERN,$(bash ./cfiojobs.normal.sh $fio_logfile)" >>$fio_outputfile
#                continue
#            else
#                :
#            fi

            #remove ssh info before analyse
            sed -i "/to the list of known hosts/d" $fio_logfile
            sed -i "/^fio:/d" $fio_logfile
            # check info missing
            if grep -q "disk_util" $fio_logfile || [[ $(cat $fio_logfile |wc -l) -gt 50 ]] ;then
                :
            else
                echo "$fio_logfile, json log info missing."
                continue
            fi
            # remove none json info
            until head -1 $fio_logfile |grep -q ^'{' ;do
                echo "json log: $fio_logfile, unknown info: \"$(head -1 $fio_logfile)\""
                echo "$fio_logfile : $(head -1 $fio_logfile)" >> $OUTPUT_DIR/fio-err.log
                sed -i 1d $fio_logfile
            done

            # deal with mixed rw
            if [[ $PATTERN == "randrw" ]] 
            then
               # if randrw mode, python script will generate the log automaticlly
               python2 $json_script $fio_logfile
               echo "mixed read and write skip single pattern anaylsing..."
               continue
            else
                #normal pattern log
                #declare -a job_info_list
                job_info_list=($(python2 $json_script $fio_logfile))
                IODEPTH="${job_info_list[5]}"
                util=${job_info_list[2]%"."*}
                #echo "iodepth:$IODEPTH util:$util"
                if [[ "$util" -lt 1 ]] ;then
                    echo -e "\e[31m value unavailable! \e[0m"
                    #IO="x"
                    IOPS="x"
                    BW="x"
                    #latency_min="x"
                    latency_max="x"
                    latency_avg="x"
                else
                    BW=${job_info_list[6]}
                    IOPS=${job_info_list[7]}
                    latency_max=${job_info_list[8]}
                    latency_avg=${job_info_list[9]}
                fi
            fi
            #output value
            #echo -e "\
            # fio $BS$PATTERN, log info
            # iodepth: $IODEPTH,
            # bw $BW
            # iops $IOPS 
            # latency: max $latency_max, min $latency_avg\n"

            #sleep 3
            [[ -f $fio_outputfile ]] || echo "bs_pattern,iodepth,bw(MiB/s),iops,latency_max(ms),latency_avg(ms)" > $fio_outputfile
            echo "$BS$PATTERN,$IODEPTH,$BW,$IOPS,$latency_max,$latency_avg" >>$fio_outputfile
        done &
        #blk
    done &
    #pattern
done
#bs
