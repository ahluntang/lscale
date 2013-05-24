#!/usr/bin/env bash
# -*- coding: utf-8 -*-
echo "Running zebra addressing script for container {{ container_id }}"
ip link set lo up
{% for interface in interfaces %}
    ip link set {{ interface }} up
{% endfor %}

cd ~/quagga/{{ container_id }}
/usr/lib/quagga/zebra -f zebra.conf --daemon -A 127.0.0.1
