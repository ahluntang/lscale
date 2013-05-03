#!/usr/bin/env bash


CONTAINER_NAME=$1
BACKING_STORE=$2


if [ $# -eq 0 ] ; then
    lxc-create -n base
    exit 0
elif [ $# -eq 1 ]; then
    lxc-create -n ${CONTAINER_NAME}
    exit 0
elif[ $# -eq 2 ]; then
    lxc-create -n ${CONTAINER_NAME} -B ${BACKING_STORE}
    exit 0
else
    echo "This script does not accept more than 2 arguments."
    exit 1
fi
