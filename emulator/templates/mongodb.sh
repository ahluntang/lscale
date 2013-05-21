#!/usr/bin/env bash

echo "-> Setting up MongoDB..."
sed -i "/bind_ip/c\bind_ip = 127.0.0.1,{{ mongodb_address }} " /etc/mongodb.conf
service mongodb restart
