from utilities import ContainerType, is_lxc

def daemons(container):
    return ""


def zebra(container):
    config = ""
    count = 0
    for interface in container.interfaces:
        if is_lxc(container.container_type):
            interface_name = "eth{}".format(count)
            count = count + 1
        else:
            interface_name = interface.interface_id
        config += "interface {}\n".format(interface_name)
        config += "  ip address {}\n".format(interface.address)
    return config


def debian(container):
    return ""


def ospf(networks, container):
    config = '!\nrouter ospf\n!'
    for network in networks:
        #addresses.append("network {} area 0".format(network))
        config += "\n    network {} area 0".format(network)
    config += "\n!\n"
    count = 0
    for interface in container.interfaces:
        if is_lxc(container.container_type):
            interface_name = "eth{}".format(count)
            count = count + 1
        else:
            interface_name = interface.interface_id
        config += "interface {}\n".format(interface_name)
        config += "    ip ospf hello-interval 1\n"
        config += "    ip ospf dead-interval 4\n"

    return config
