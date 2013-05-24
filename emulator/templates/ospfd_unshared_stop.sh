#!/usr/bin/env bash

cd ~/quagga/{{ container_id }}

kill -9
rm pid.conf
