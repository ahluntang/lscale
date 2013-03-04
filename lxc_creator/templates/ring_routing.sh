#!/usr/bin/env bash
# -*- coding: utf-8 -*-

echo "Running ring_routing script for container {{ container_id }}"

echo "Setting ip address {{ if0_address }} for {{ if0 }}"
ip address add {{ if0_address }} dev {{ if0 }}
ip link set {{ if0 }} up

echo "Setting ip address {{ if1_address }} for {{ if1 }}"
ip address add {{ if1_address }} dev {{ if1 }}
ip link set {{ if1 }} up

echo "Enabling routing"
sysctl -w net.ipv4.ip_forward=1

{% for route in routes %}
    ip route add {{ route.address }} dev {{ route.interface }}
{% endfor %}