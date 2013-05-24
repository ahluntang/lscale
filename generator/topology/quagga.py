def daemons(container):
    return ""


def zebra(container):
    config = ""
    for interface in container.interfaces:
        config += "interface {}\n".format(interface.interface_id)
        config += "  ip address {}\n".format(interface.address)
    return config


def debian(container):
    return ""


def ospf(networks, container):
    config = '!\nrouter ospf\n!'
    for network in networks:
        #addresses.append("network {} area 0".format(network))
        config += "\n    network {} area 0".format(network)
    config +="\n!\n"
    for interface in container.interfaces:

        config += "interface {}\n".format(interface.interface_id)
        config += "    ip ospf hello-interval 1\n"
        config += "    ip ospf dead-interval 4\n"

    return config
