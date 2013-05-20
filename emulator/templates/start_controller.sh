#!/usr/bin/env bash

{% for node, ip in nodes.items() %}
    #{{ node }} : {{ ip }}
{% endfor %}

SCRIPT_NAME="rftest2"
LXCDIR=/var/lib/lxc
MONGODB_CONF=/etc/mongodb.conf
RF_HOME=RouteFlow

export PATH=$PATH:/usr/local/bin:/usr/local/sbin
export PYTHONPATH=$PYTHONPATH:$RF_HOME

cd $RF_HOME

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


echo_bold "-> Setting up MongoDB..."
sed -i "/bind_ip/c\bind_ip = 127.0.0.1,{{ mongodb_address }}" $MONGODB_CONF
service mongodb restart
wait_port_listen {{ mongodb_port }}

echo_bold "-> Starting the controller and RFPRoxy..."
cd pox
./pox.py log.level --=INFO topology openflow.topology openflow.discovery rfproxy rfstats &
cd -
wait_port_listen {{ controller_port }}

echo_bold "-> Creating rfconfig.csv ... "

VM_ID=0
VM_PORT=1
CT_ID=0
DP_ID=0
DP_PORT=1
echo "vm_id,vm_port,ct_id,dp_id,dp_port" > rfconfig.csv
{% for container_name, interfaces in dpinterfaces.items() %}
    {% for interface, mac in interfaces.items() %}
        echo "{{ mac }},${VM_PORT},${CT_ID},${DP_ID},${DP_PORT}" >> rfconfig.csv
        VM_PORT=$[$VM_PORT+1]
        DP_PORT=$[DP_PORT+1]
    {% endfor %}
    VM_PORT=1
    DP_PORT=1
{% endfor %}



echo_bold "-> Starting RFServer..."
./rfserver/rfserver.py rfconfig.csv &


echo_bold "-> Starting the control plane network (dp0 VS)..."
ovs-vsctl --may-exist add-br dp0
{% for container_name, interfaces in dpinterfaces.items() %}
    {% for interface, mac in interfaces.items() %}
        ovs-vsctl add-port dp0 {{ interface }}
    {% endfor %}
{% endfor %}


echo_bold "-> adding controller to dp0"
ovs-vsctl set Bridge dp0 other-config:datapath-id=7266767372667673
ovs-vsctl set-controller dp0 tcp:127.0.0.1:{{ controller_port }}
