from flufl.enum import Enum

ContainerType = Enum('ContainerType', 'NONE UNSHARED LXC LXCLVM')

BridgeType = Enum('BridgeType', 'BRIDGE OPENVSWITCH')


