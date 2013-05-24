def daemons(container):
    return ""


def zebra(container):
    return ""


def debian(container):
    return ""


def ospf(component):
    config = 'router ospf'
    for address in component.addresses:
        #addresses.append("network {} area 0".format(address))
        config += "\n\tnetwork {} area 0".format(address)

    return config
