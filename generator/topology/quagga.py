def daemons(container):
    return ""


def zebra(container):
    return ""


def debian(container):
    return ""


def ospf(networks):
    config = 'router ospf'
    for network in networks:
        #addresses.append("network {} area 0".format(network))
        config += "\n    network {} area 0".format(network)

    return config
