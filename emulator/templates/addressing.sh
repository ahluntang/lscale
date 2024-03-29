#!/usr/bin/env bash
# -*- coding: utf-8 -*-
echo "Running addressing script for container {{ container_id }}"
ip link set lo up
{% for interface in interfaces %}
    ip link set {{ interface }} up
{% endfor %}
{% for address in addresses %}
    ip address add {{ address.address }} brd + \
    dev {{ address.interface }}
    ip link set {{ address.interface }} up
{% endfor %}

echo "SCRIPTFINISHED"
