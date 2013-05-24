#!/usr/bin/env bash

cd ~
mkdir quagga
cd quagga
mkdir {{ container_id }}
cd {{ container_id }}

cat > zebra.conf <<EOF
{{ zebra }}
EOF


cat > ospfd.conf <<EOF
{{ ospf }}
EOF



echo "SCRIPTFINISHED"
