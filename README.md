# cfiojobs
cluster fio jobs distributer.

This script is a simple fio jobs and file distributer, you can also send commands to multy hosts with it.

Remanber, you need passwordless ssh access permitions to all hosts, and use a comma as a delimiter when you have multiple group units.

usage :
1. Edit your own host group, block group and fio job type settings in config files.

   (1)     hosts  list conf:
   
               ./cfiojobs.grp
   
   (2)     blocks list conf:
   
               ./cfiojobs.blk
   
   (3)     jobs   list conf:
   
               ./cfiojobs.job
   

   tips: './cfiojobs -e' will generate example configure files for you
   

2. Run a short single cmd: 

       ./cfiojobs <options> [commands]
   
   options: 
   
           -t            check host group config file format.
           
           -g group      send commands to certain group in ./cfiojobs.grp
           
           -a            send commands to all group set
           
           -x host       send commands except given hosts
           
           -X group      send commands except given host groups
           
           -q            return only command exit status.(be quiet and less output if no error occurred)
           
           -d            check function parameters on running and skip failue
           
           -f            skip failure and try to continue, if possible
           
           -p            send command and copy files execute in parallel
           

   example: 

           ./cfiojobs -q -g grp1,grp2,grp3,grp4 "systemctl status sshd ;ls abc" -x 172.16.0.105
   
   tips:
      
      say you want run the command:
      
              'ls -i' 
              
      you can use: 
      
              ./cfiojobs ls -i -g vmg1,grp3 -t -d
              
      it is fine, because '-i' does not confilict with any options supported by this script,
      
      but still we strongly recommend you write it this way:
      
              ./cfiojobs "ls -i" -g vmg1,grp3 -t -d
              

3. Example of Some more complex situation. (how to use double/single quote to pass the complete cmd to script):

   (1). with multy command a time:  
   
               ./cfiojobs "command1 ;  command2 ;  command3 "
   
   (-1) with command list to run :  
   
               ./cfiojobs "command1 && command2 || command3 "
        
   (2). with pipe thing or some  :  
   
               ./cfiojobs "your command |pipe |pipe "
   
   (3). with local bash variable :  
   
               ./cfiojobs "your command $local_variable "
   
   (4). with remote env variable :  
   
               ./cfiojobs "your command '$remote_env_viriable' " 
   

   example: 
   
               ./cfiojobs -g grp1 "ls -l |awk '{print\$2}'"
   
   or: 
   
               ./cfiojobs -g grp1 "ls -l |awk \"{print\\\$2}\""
         
   tips: awk variable is not shell variable, so there were three antislash inside curly braces,
         first two antislash passed an '\' to remote bash, and then the third is for the translating of the '$'.
            

4. FIO jobs control

   options:
   
           --fio         launch a fio test

           --test-stop   stop test on given host groups(stop all test and all jobs)

           --fio-stop    stop all existinging fio jobs on given host groups (stop a round of jobs of a test)

           --fio-list    output summary info of fio jobs on given host groups
           
           -b            send fio job with given blk group in ./cfiojobs.blk
           
           -j            send fio job with given job group in ./cfiojobs.job
           
           -A            fio task 'After' commands that you give
           
           -o            set the output dir of fio test logs.
           
           -s            single mode, one block a time.
           
           -l            list all running fio jobs info.
           

   example: 
   
          ./cfiojobs --fio-list -g group1 -q
   
          ./cfiojobs --fio -g grp1 -b vd5 -j rand1,mix1 -A "umount /dev/vdb"
            
      tips:
      
      when send commands along with fio jobs to a host, they will be execute parallelly,
      
      fio jobs will be send first by default, you can use '-A' to let command execute first.
      

5. File distribution

   options:
   
           -F file       copy files to remote host

           -C file       collect files from remote to local host

           -D dir        specify destination directory on remote host
           

   example: 
   
          ./cfiojobs -g grp1 -F file1,file2,file3 -D /tmp/180730/ -x 172.16.0.137
   

6. Help info

   options:
   
           -h            show this help info
           
           -e            make example config files (when they do not exist)
           
