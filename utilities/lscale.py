from flufl.enum import Enum

ContainerType = Enum('ContainerType', 'NONE UNSHARED LXC LXCLVM')

BridgeType = Enum('BridgeType', 'BRIDGE OPENVSWITCH')


def is_lxc(container):
    return \
        container == ContainerType.LXC or \
        container == ContainerType.LXCLVM
