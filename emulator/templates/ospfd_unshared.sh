#!/usr/bin/env bash

cd ~/quagga/{{ container_id }}
/usr/lib/quagga/ospfd -f ospfd.conf -A 127.0.0.1

echo "SCRIPTFINISHED"
