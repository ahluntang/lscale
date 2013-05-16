#!/usr/bin/env bash

VOLUMEGROUP=${1}

DEVICE=${2}  #"/dev/sda"

PARTITION=${3} # 4

CACHE=${4}
LIB=${5}

add_line_to_config() {
    line=$1
    file=$2
    if grep -Fxq "${line}" ${file}
    then
        echo "${line} already in ${file}, skipping..."
    else
        echo "${line}" | tee -a ${file}
    fi
}

aptitude -y install lvm2

# Changes type of /dev/sda4 to 8e (Linux LVM)
echo "t
${PARTITION}
8e
w" | fdisk ${DEVICE}

# inform linux kernel of new changes in disk
partprobe

# initialize the LVM partition as a Physical Volume
pvcreate /dev/sda4


# creating lxc volume group
vgcreate  ${VOLUMEGROUP} ${DEVICE}${PARTITION}

if [ ${CACHE} -eq 0 ]
then
    echo "No cache size specified."

else
    # creating logical volume cache in volume group lxc
    lvcreate -n cache -L ${CACHE}G ${VOLUMEGROUP}
    lvcreate -n lib -L ${LIB}G ${VOLUMEGROUP}

    lmke2fs -t ext4 /dev/lxc/cache
    lmke2fs -t ext4 /dev/lxc/lib

    # backup existing cache folder
    mv /var/cache/lxc /var/cache/lxc.old
    mv /var/lib/lxc /var/lib/lxc.old

    # create new empty cache folder, add mount info to fstab and mount it.
    mkdir /var/cache/lxc
    mkdir /var/lib/lxc
    add_line_to_config '/dev/${VOLUMEGROUP}/cache /var/cache/lxc ext4 errors=remount-ro 0 1' '/etc/fstab'
    add_line_to_config '/dev/${VOLUMEGROUP}/lib /var/lib/lxc ext4 errors=remount-ro 0 1' '/etc/fstab'
    mount -a /dev/${VOLUMEGROUP}/cache
    mount -a /dev/${VOLUMEGROUP}/lib
fi
