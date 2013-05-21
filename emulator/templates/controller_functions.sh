#!/usr/bin/env bash

SCRIPT_NAME="rftest2"
LXCDIR=/var/lib/lxc
MONGODB_CONF=/etc/mongodb.conf
RF_HOME=RouteFlow


cd $RF_HOME


export PATH=$PATH:/usr/local/bin:/usr/local/sbin
export PYTHONPATH=$PYTHONPATH:.
#make clean
make rfclient

wait_port_listen() {
    port=$1
    while ! `nc -z localhost $port` ; do
        echo -n .
        sleep 1
    done
}

echo_bold() {
    echo -e "\033[1m${1}\033[0m"
}

kill_process_tree() {
    top=$1
    pid=$2

    children=`ps -o pid --no-headers --ppid ${pid}`

    for child in $children
    do
        kill_process_tree 0 $child
    done

    if [ $top -eq 0 ]; then
        kill -9 $pid &> /dev/null
    fi
}

echo_bold "-> Setting up the management bridge (lxcbr0)..."
ifconfig lxcbr0 ${1} up

echo "-> Setting up MongoDB..."
#sed -i "/bind_ip/c\bind_ip = 127.0.0.1,${1}" $MONGODB_CONF
#service mongodb restart
#wait_port_listen ${2}
sleep 10
echo_bold "-> Starting the controller and RFPRoxy..."
cd pox
./pox.py log.level --=INFO topology openflow.topology openflow.discovery rfproxy rfstats &
cd -
#wait_port_listen ${3}
sleep 10

#echo_bold "-> Creating rfconfig.csv ... "
