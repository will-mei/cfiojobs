
This script is a simple fio jobs and file distributer, you can also run commands on multy hosts with it.
Remanber, you need passwordless ssh access permitions to all hosts, and use a comma as a delimiter when you have multiple group units.

usage :
1. Edit your own host group, block group and fio job type settings in config files.
   (1)     hosts  list conf:   ./cfiojobs.grp
   (2)     blocks list conf:   ./cfiojobs.blk
   (3)     jobs   list conf:   ./cfiojobs.job

   tips: './cfiojobs -e' will generate example configure files for you

2. Run a short single cmd: 
   ./cfiojobs <options> [commands]
   options: 
           -t            check host group config file format.
           -g group      run commands on certain groups in ./cfiojobs.grp
           -a            run commands on all groups set
           -x host       make an exception on these hosts
           -X group      make an exception on these host groups 
           -q            return only exit status of command.(be quiet and less output if no error occurred)
           -d            check and give function parameters, also, skip failue
           -f            skip failure and try to continue, if possible
           -p            send commands and copy files execute in parallel

   example: ./cfiojobs -q -g grp1,grp2,grp3,grp4 "systemctl status sshd ;ls abc" -x 172.18.211.105
      tips:
      say you want run the command:
              'ls -i' 
      you can use: 
              ./cfiojobs ls -i -g vmg1,grp3 -t -d
      it is fine, because '-i' does not confilict with any options supported by this script,
      but still we strongly recommend you write it this way:
              ./cfiojobs "ls -i" -g vmg1,grp3 -t -d

3. Example of Some more complex situation. (how to use double/single quote to pass the complete cmd to script):
   (1). with multy command a time:  ./cfiojobs "command1 ;  command2 ;  command3 "
        with command list to run :  ./cfiojobs "command1 && command2 || command3 "
   (2). with pipe thing or some  :  ./cfiojobs "your command |pipe |pipe "
   (3). with local bash variable :  ./cfiojobs "your command $local_variable "
   (4). with remote env variable :  ./cfiojobs "your command '$remote_env_viriable' " 

   example: ./cfiojobs -g grp1 "ls -l |awk '{print\$2}'"
         or ./cfiojobs -g grp1 "ls -l |awk \"{print\\\$2}\""
      tips: awk variable is not shell variable, so there were three antislash inside curly braces,
            first two antislash passed an '\' to remote bash, and then the third is for the translating of the '$'.

4. FIO jobs control
   options:
           --fio         launch a fio test
           --test-stop   stop test on given host groups(stop all test and all jobs)
           --fio-stop    stop all existinging fio jobs on given host groups (stop a round of jobs of a test)
           --fio-list    output summary info of fio jobs on given host groups
           -b            run fio jobs with given blk group in ./cfiojobs.blk
           -j            run fio job with given job group in ./cfiojobs.job
           -A            fio task 'After' commands that are given
           -o            set the output dir for all fio test logs.
           -s            single mode, one block a time.
           -l            list all running fio jobs info.

   example: ./cfiojobs --fio-list -g group1 -q
            ./cfiojobs --fio -g grp1 -b vd5 -j rand1,mix1 -A "umount /dev/vdb"
      tips:
      when both the commands and fio jobs were running on a given host, they will be execute in parallel,
      but fio jobs will be send first by default, you can use '-A' to let command execute first.

5. File distribution
   options:
           -F file       copy files to remote host
           -C file       collect files from remote to local host
           -D dir        specify destination directory on remote host

   example: ./cfiojobs -g grp1 -F file1,file2,file3 -D /tmp/180730/ -x 172.18.211.137

6. Help info
   options:
           -h            show this help info
           -e            make examples of config file (when they do not exist)

