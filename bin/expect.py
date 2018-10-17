#!/usr/bin/env python
# coding=utf-8
import sys 
import pexpect

try:
    sshuser    = sys.argv[1]
    sshpwd     = sys.argv[2]
    sshport    = sys.argv[3]
    command    = sys.argv[4:]
except IndexError:
    print("no enough args!\n1.username \n2.pwd \n3.port \n4.command")
    exit()

print(sshuser,sshpwd,sshport,command)
