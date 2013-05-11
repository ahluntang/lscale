from flufl.enum import Enum


ContainerType = Enum('ContainerType', 'NONE UNSHARED LXC LXCLVM')
BridgeType = Enum('BridgeType', 'BRIDGE OPENVSWITCH')

def is_lxc(container_type):
    return \
        container_type == ContainerType.LXC or \
        container_type == ContainerType.LXCLVM
