#!/usr/bin/env bash

cd ~
mkdir quagga
cd quagga
mkdir {{ container_id }}
cd {{ container_id }}

cat > ospfd.conf << EOF
{{ ospf }}
EOF


echo "SCRIPTFINISHED"
