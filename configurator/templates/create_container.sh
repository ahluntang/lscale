#!/usr/bin/env bash


CONTAINER_NAME=$1
BACKING_STORE=$2
TEMPLATE=$3


if [ $# -eq 0 ]
then
    echo "Creating container base with template ubuntu using no backingstore"
    lxc-create -n base -t ubuntu -B none
    exit 0
elif [ $# -eq 1 ]
then
    echo "Creating container  ${CONTAINER_NAME} with template ubuntu using no backingstore"
    lxc-create -n ${CONTAINER_NAME}  -t ubuntu -B none
    exit 0
elif [ $# -eq 2 ]
then
    echo "Creating container  ${CONTAINER_NAME} with template ubuntu using ${BACKING_STORE} as backingstore"
    lxc-create -n ${CONTAINER_NAME} -B ${BACKING_STORE}  -t ubuntu
    exit 0
elif [ $# -eq 3 ]
then
    echo "Creating container  ${CONTAINER_NAME} with template ${TEMPLATE} using ${BACKING_STORE} as backingstore"
    lxc-create -n ${CONTAINER_NAME} -B ${BACKING_STORE}  -t ${TEMPLATE}
    exit 0
else
    echo "This script does not accept more than 3 arguments."
    exit 1
fi
