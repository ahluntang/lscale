#!/usr/bin/env bash

cd ~
mkdir quagga
cd quagga
mkdir {{ container_id }}
cat > daemons << EOF
{{ daemons }}
EOF

cat > debian.conf << EOF
{{ debian }}
EOF

cat > ospfd.conf << EOF
{{ ospf }}
EOF

cat > zebra.conf << EOF
{{ zebra }}
EOF


echo "SCRIPTFINISHED"
