#!/usr/bin/env bash

cd ~/quagga/{{ container_id }}

/usr/lib/quagga/ospfd -f ospfd.conf -i pid.conf -d

echo "SCRIPTFINISHED"
