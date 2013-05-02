#!/usr/bin/env bash
# -*- coding: utf-8 -*-


#ssh_pids=(`pidof sshd | tr " " "\n"`)


#main_ssh=`cat /var/run/sshd.pid`

#echo $main_ssh

#for pid in "${ssh_pids[@]}"
#do
#	if [ "$pid" == "$main_ssh" ]
#	then
#	    echo Not killing main ssh: $pid
#	else
#	    echo Killing ssh with pid $pid
#	    sudo kill $pid
#	fi
#done
