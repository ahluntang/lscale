#!/usr/bin/env bash
# -*- coding: utf-8 -*-

echo "Running ring_routing script for container {{ container_id }}"


ip link set lo up

{% for address in addresses %}
    ip address add {{ address.address }} brd + \
    dev {{ address.interface }}
    ip link set {{ address.interface }} up
{% endfor %}

echo "Enabling routing"
sysctl -w net.ipv4.ip_forward=1

route add default gw {{ gateway.address }} {{ gateway.interface }}

{% for route in routes %}
    ip route add {{ route.address }} \
    via {{ route.via }} dev {{ route.interface }}
{% endfor %}
