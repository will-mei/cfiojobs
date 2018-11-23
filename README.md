**This script is a simple fio jobs and file distributor. You can also run
commands on multiple hosts with it.**

**Remenber, you need passwordless SSH access permssions for all hosts, and use a
comma as a delimiter when you have multiple group units.**

usage :
=======

1. Edit your own host group, block group and fio job type settings in config files.
-----------------------------------------------------------------------------------

**(1) hosts list conf: ./cfiojobs.grp**

**(2) blocks list conf: ./cfiojobs.blk**

**(3) jobs list conf: ./cfiojobs.job**

*tips: './cfiojobs -e' will generate example configure files for you*

2. Run a short single cmd: 
---------------------------

./cfiojobs \<options\> [commands]

options:

**-t check host group config file format.**

**-g groups run commands on certain host groups in ./cfiojobs.grp (sep with
comma)**

**-a run commands on all host group set**

**-x hosts make an exception on these hosts (sep with comma)**

**-X groups make an exception on these host groups (sep with comma)**

**-q return only exit status of command.(be quiet and less output if no error
occurred)**

**-d check and give function parameters, also, skip failure**

**-f skip failure and try to continue, if possible**

**-p send commands and copy files execute in parallel**

*Example: ./cfiojobs -q -g grp1,grp2,grp3,grp4 "systemctl status sshd ;ls abc"
-x 172.18.211.105*

*tips:*

*say you want run the command:*

*'ls -i'*

*you can use:*

*./cfiojobs ls -i -g vmg1,grp3 -t -d*

*it is fine, because '-i' does not confilict with any options supported by this
script,*

*but still we strongly recommend you write it this way:*

*./cfiojobs "ls -i" -g vmg1,grp3 -t -d*

3. Example of Some more complex situation. (how to use double/single quote to pass the complete cmd to script):
---------------------------------------------------------------------------------------------------------------

(1).with multy command a time:

**./cfiojobs -g \<grp name\> "command1 ; command2 ; command3 "**

with command list to run :

**./cfiojobs -g \<grp name\> "command1 && command2 \|\| command3 "**

(2).with pipe thing or some :

**./cfiojobs -g \<grp name\> "your command \|pipe \|pipe "**

(3).with local bash variable :

**./cfiojobs -g \<grp name\> "your command \$local_variable "**

(4).with remote env variable :

**./cfiojobs -g \<grp name\> "your command '\$remote_env_viriable' "**

*example:*

*./cfiojobs -g grp1 "ls -l \|awk '{print\\\$2}'"*

*or:*

*./cfiojobs -g grp1 "ls -l \|awk \\"{print\\\\\\\$2}\\""*

*tips: awk variable is not bash shell variable, so there were three antislash
inside curly braces,*

*first two antislash passed an '\\' to remote bash, and then the third is for
translating the '\$'.*

4. FIO jobs control
-------------------

options:

**--fio launch a fio test**

**--fio-list output summary info of fio jobs on given host groups**

**--fio-stop stop all existinging fio jobs on given host groups (stop a certain
round of jobs in test)**

**--test-stop stop test on given host groups (stop all test and all jobs)**

**--recover recover an undone test form where it was interrupted (aborted,
killed or cancled)**

**--recover-from recover or restart the test form a given "round number" (and a
certain "blk group")**

**--round-list list all job round info with your test options and arguments
(launch no test)**

**--round-retest retest a batch of fio jobs with a given "blk group name" and
"round number"**

**the round range like: "6-9" or: "blk8,6-9" are both ok.**

**-c check test env, (network, ssh connections, fio installation, blk dev to
test)**

**-b run fio jobs with given blk group in ./cfiojobs.blk**

**-j run fio job with given job group in ./cfiojobs.job**

**-A fio task 'After' commands that are given**

**-E run the commands everythime fio test batch starts on a host**

**-o set the output dir for all fio test logs.**

**-s single block mode, one block a time on each host.**

**-S single group mode, one group a time in the test.**

**-l list all running fio jobs info.**

**-r test on rbd blk.**

*example:*

*./cfiojobs --fio -g grp1 -b vd5,blk8 -j rand1 -o test01*

*./cfiojobs --fio-list -g group1 -p*

*you can have the current round info from script stdout or log file:
"\<output_dir\>/recover.log", you can easyly*

*recover the test with with a certin round point in test progress, say, to
recover the previous test with blk*

*target "blk8" and round "6", you can use the command :*

*./cfiojobs --fio -g grp1 -b vd5,file8 -j rand1 --recover-from blk8,6 -o test01*

*or recover a test with only one blk group:*

*./cfiojobs --fio -g grp1 -b vd5 -j rand1,mix1 --recover-from 6 -f -o test02*

*or recover the test from where you don't know:*

*./cfiojobs --fio -g grp1 -b vd5 -j rand1,mix1 --recover -f -o test02*

*note:*

*when both the commands and fio jobs were running on a given host, they will be
execute in parallel,*

*but fio jobs will be send first by default, you can use '-A' to let command
execute first.*

*./cfiojobs --fio -g grp1 -b vd5,blk8 -j rand1,mix1 -A "umount /dev/vdb" -o
grp1_parallel_test01*

tips:

*remanber to check the test env befor you start your fio test on a group:*

*./cfiojobs -g \<group name\> -f -c*

5. File distribution
--------------------

options:

**-F files copy files(sep with comma) to remote host**

**-C files collect files(sep with comma) from remote to local host**

**-D dir specify destination directory on remote host**

*example: ./cfiojobs -g grp1 -F file1,file2,file3 -D /tmp/180730/ -x
172.18.211.137*

6. Help info
------------

options:

**-h show this help info**

**-e make examples of config file (when they do not exist)**

**-v, --version show version info**
