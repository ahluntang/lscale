#!/usr/bin/env bash
# -*- coding: utf-8 -*-

echo "Running star_routing script for container {{ container_id }}"


ip link set lo up

{% for address in addresses %}
    ip address add {{ address.address }} dev {{ address.interface }}
    ip link set {{ address.interface }} up
{% endfor %}
