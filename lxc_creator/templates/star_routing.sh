#!/usr/bin/env bash
# -*- coding: utf-8 -*-

echo "Running star_routing script for container {{ container_id }}"

echo "Setting ip address {{ if0_address }} for {{ if0 }}"
ip address add {{ if0_address }} dev {{ if0 }}
ip link set {{ if0 }} up
