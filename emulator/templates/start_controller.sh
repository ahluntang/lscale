#!/usr/bin/env bash

{% for node, ip in nodes.items() %}
    #{{ node }} : {{ ip }}
{% endfor %}


./emulator/templates/controller_functions.sh {{ mongodb_address }} {{ mongodb_port }} {{ controller_port }}

cd RouteFlow
export PATH=$PATH:/usr/local/bin:/usr/local/sbin
export PYTHONPATH=$PYTHONPATH:.

echo "-> Creating rfconfig.csv ... "

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



echo "-> Starting RFServer..."
./rfserver/rfserver.py rfconfig.csv &


echo "-> Starting the control plane network (dp0 VS)..."
ovs-vsctl add-br dp0

{% for container_name, interfaces in dpinterfaces.items() %}
    {% for interface, mac in interfaces.items() %}
        ovs-vsctl add-port dp0 {{ interface }}
    {% endfor %}
{% endfor %}


echo "-> adding controller to dp0"
ovs-vsctl set Bridge dp0 other-config:datapath-id=7266767372667673
ovs-vsctl set-controller dp0 tcp:127.0.0.1:{{ controller_port }}
