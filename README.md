
<br>This script is a simple fio jobs and file distributer, you can also run commands on multy hosts with it.
<br>Remanber, you need passwordless ssh access permitions to all hosts, and use a comma as a delimiter when you have multiple group units.
<br>
<br>usage :
<br>1. Edit your own host group, block group and fio job type settings in config files.
<br>    (1)     hosts  list conf:   ./cfiojobs.grp
<br>    (2)     blocks list conf:   ./cfiojobs.blk
<br>    (3)     jobs   list conf:   ./cfiojobs.job
<br>
<br>    tips: './cfiojobs -e' will generate example configure files for you
<br>
<br>2. Run a short single cmd: 
<br>    ./cfiojobs <options> [commands]
<br>    options: 
<br>            -t             check host group config file format.
<br>            -g group       run commands on certain groups in ./cfiojobs.grp
<br>            -a             run commands on all groups set
<br>            -x host        make an exception on these hosts
<br>            -X group       make an exception on these host groups 
<br>            -q             return only exit status of command.(be quiet and less output if no error occurred)
<br>            -d             check and give function parameters, also, skip failue
<br>            -f             skip failure and try to continue, if possible
<br>            -p             send commands and copy files execute in parallel
<br>
<br>   example: ./cfiojobs -q -g grp1,grp2,grp3,grp4 "systemctl status sshd ;ls abc" -x 172.18.211.105
<br>      tips:
<br>      say you want run the command:
<br>            'ls -i' 
<br>      you can use: 
<br>            ./cfiojobs ls -i -g vmg1,grp3 -t -d
<br>      it is fine, because '-i' does not confilict with any options supported by this script,
<br>      but still we strongly recommend you write it this way:
<br>            ./cfiojobs "ls -i" -g vmg1,grp3 -t -d
<br>
<br>3. Example of Some more complex situation. (how to use double/single quote to pass the complete cmd to script):
<br>    (1).with multy command a time:  
<br>            ./cfiojobs "command1 ;  command2 ;  command3 "
<br>        with command list to run :  
<br>            ./cfiojobs "command1 && command2 || command3 "
<br>    (2).with pipe thing or some  :  
<br>            ./cfiojobs "your command |pipe |pipe "
<br>    (3).with local bash variable :  
<br>            ./cfiojobs "your command $local_variable "
<br>    (4).with remote env variable :  
<br>            ./cfiojobs "your command '$remote_env_viriable' " 
<br>
<br>    example: 
<br>            ./cfiojobs -g grp1 "ls -l |awk '{print\$2}'"
<br>         or: 
<br>            ./cfiojobs -g grp1 "ls -l |awk \"{print\\\$2}\""
<br>       tips: awk variable is not shell variable, so there were three antislash inside curly braces,
<br>            first two antislash passed an '\' to remote bash, and then the third is for the translating of the '$'.
<br>
<br>4. FIO jobs control
<br>    options:
<br>            --fio          launch a fio test
<br>            --test-stop    stop test on given host groups(stop all test and all jobs)
<br>            --fio-stop     stop all existinging fio jobs on given host groups (stop a round of jobs of a test)
<br>            --fio-list     output summary info of fio jobs on given host groups
<br>            --recover      recover an undone test form where it was interrupted (aborted, killed or cancled)
<br>            --recover-from recover or restart the test form a given "round number" (and a certain "blk group")
<br>            --round-list   list all job round info with your test options and arguments
<br>            --round-retest retest a batch of jobs with a given "round number" (and a certain "blk group")
<br>            -c             check test env, (network, ssh connections, fio installation, blk dev to test)
<br>            -b             run fio jobs with given blk group in ./cfiojobs.blk
<br>            -j             run fio job with given job group in ./cfiojobs.job
<br>            -A             fio task 'After' commands that are given
<br>            -E             run the commands everythime fio test batch starts on a host 
<br>            -o             set the output dir for all fio test logs.
<br>            -s             single mode, one block a time.
<br>            -l             list all running fio jobs info.
<br>
<br>    example: 
<br>            ./cfiojobs --fio -g grp1 -b vd5,blk8 -j rand1 -o test01 
<br>            ./cfiojobs --fio-list -g group1 -p
<br>        you can have the current round info from script stdout or log file: "<output_dir>/recover.log", you can easyly 
<br>        recover the test with with a certin round point in test progress, say, to recover the previous test with blk 
<br>        target "blk8" and round "6", you can use the command :         
<br>            ./cfiojobs --fio -g grp1 -b vd5,file8 -j rand1 --recover-from blk8,6 -o test01 
<br>        or recover a test with only one blk group:
<br>            ./cfiojobs --fio -g grp1 -b vd5 -j rand1,mix1 --recover-from 6 -f -o test02 
<br>        or recover the test from where you don't know:
<br>            ./cfiojobs --fio -g grp1 -b vd5 -j rand1,mix1 --recover -f -o test02 
<br>    note:
<br>        when both the commands and fio jobs were running on a given host, they will be execute in parallel,
<br>        but fio jobs will be send first by default, you can use '-A' to let command execute first.
<br>            ./cfiojobs --fio -g grp1 -b vd5,blk8 -j rand1,mix1 -A "umount /dev/vdb" -o grp1_parallel_test01
<br>
<br>    tips:
<br>        remanber to check the test env befor you start your fio test on a group:
<br>            ./cfiojobs -g <group name> -f -c
<br>
<br>5. File distribution
<br>    options:
<br>            -F file        copy files to remote host
<br>            -C file        collect files from remote to local host
<br>            -D dir         specify destination directory on remote host
<br>
<br>    example: ./cfiojobs -g grp1 -F file1,file2,file3 -D /tmp/180730/ -x 172.18.211.137
<br>
<br>6. Help info
<br>    options:
<br>            -h             show this help info
<br>            -e             make examples of config file (when they do not exist)
<br>            -v, --version  show version info
<br>
<br>
