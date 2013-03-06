#!/usr/bin/env bash
# -*- coding: utf-8 -*-

echo "Running ring_routing script for container {{ container_id }}"


ip link set lo up

{% for address in addresses %}
    ip address add {{ address.address }} dev {{ address.interface }}
    ip link set {{ address.interface }} up
{% endfor %}

echo "Enabling routing"
sysctl -w net.ipv4.ip_forward=1

ip route add default dev {{ gateway }}

{% for route in routes %}
    ip route add {{ route.address }} dev {{ route.interface }}
{% endfor %}
