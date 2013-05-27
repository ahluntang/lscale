#!/usr/bin/env bash

START=${1}
STOPPED=`sudo lxc-list | sed '0,/STOPPED/d;/base*/d;/lost+found/d;/quagga/d'`


for CONTAINER in "${STOPPED[@]}"
do
    sudo ip link | grep pfifo_fast | cut -d: -f2 | grep ${CONTAINER} | xargs -n 1 sudo  ip link del
    if [[ ${START} == "START" ]]
    then
        sudo lxc-start -dn ${CONTAINER}
    fi
done
