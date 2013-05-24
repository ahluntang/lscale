#!/usr/bin/env bash

cat > /etc/quagga/daemons <<EOF
{{ daemons }}
EOF

cat > /etc/quagga/debian.conf <<EOF
{{ debian }}
EOF

cat > /etc/quagga/ospfd.conf <<EOF
{{ ospf }}
EOF

cat > /etc/quagga/zebra.conf <<EOF
{{ zebra }}
EOF


echo "SCRIPTFINISHED"
