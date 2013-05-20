#!/usr/bin/env bash

cd RouteFlow

aptitude -y install build-essential git libboost-dev libboost-program-options-dev libboost-thread-dev libboost-filesystem-dev iproute-dev openvswitch-switch mongodb python-pymongo


./build.sh -c ${1}
