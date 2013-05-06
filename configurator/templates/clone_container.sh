#!/usr/bin/env bash

CONTAINER_NAME=$1
ORIGINAL_CONTAINER=$2
SNAPSHOT=$3


if [ $# -eq 0 || $# -eq 1 ] ; then
    echo "This script requires two or three arguments."
elif [ $# -eq 2 ]; then
    lxc-clone -o ${ORIGINAL_CONTAINER} -n ${CONTAINER_NAME}
    exit 0
elif[ $# -eq 3 ]; then
    lxc-clone -o ${ORIGINAL_CONTAINER} -n ${CONTAINER_NAME} -s
    exit 0
else
    echo "This script does not accept more than 3 arguments."
    exit 1
fi
