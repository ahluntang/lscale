#!/usr/bin/env bash


add_line_to_config() {
    line=$1
	file=$2
	if grep -Fxq "${line}" ${file}
	then
	    echo "${line} already in ${file}, skipping..."
	else
	    echo "${line}" | tee -a ${file}
	fi
}


echo "installing required packages"
aptitude -y install bridge-utils openvswitch-datapath-source

echo "build and install open vswitch datapath"
module-assistant auto-install openvswitch-datapath


echo "installing the rest"
aptitude -y install openvswitch-brcompat openvswitch-common

echo "configuring system"
add_line_to_config 'BRCOMPAT=yes' '/etc/default/openvswitch-switch'
add_line_to_config 'blacklist bridge' '/etc/modprobe.d/blacklist.conf'

echo "removing bridge module"
# remove the default bridge module from kernel
rmmod bridge


echo "start openvswitch"
/etc/init.d/openvswitch-switch restart
ovs-vsctl add-br lxcbr0
