from flufl.enum import Enum


ContainerType = Enum('ContainerType', 'NONE UNSHARED UNSHAREDMOUNT LXC LXCCLONE')
BridgeType = Enum('BridgeType', 'BRIDGE OPENVSWITCH')
BackingStore = Enum('BackingStore', 'NONE LVM BTRFS')

def is_lxc(container_type):
    return \
        container_type == ContainerType.LXC or \
        container_type == ContainerType.LXCCLONE
