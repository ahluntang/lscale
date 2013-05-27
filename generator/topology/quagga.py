from utilities import ContainerType, is_lxc

def daemons(container):
    return ""


def zebra(container):

    config = 'password routeflow\n'
    config += 'enable password routeflow\n'
    config += 'password 123\n'
    config += 'enable password 123\n'
    count = 1
    for interface in container.interfaces:
        if is_lxc(container.container_type):
            interface_name = "eth{}".format(count)
            count += 1
        else:
            interface_name = interface.interface_id
        config += "interface {}\n".format(interface_name)
        config += "  ip address {}\n".format(interface.address)
    return config


def debian(container):
    return ""


def ospf(networks, container):
    config = 'password routeflow\n'
    config += 'enable password routeflow\n'
    config += '!\nrouter ospf\n!'
    config += '    ospf router-id {}\n'.format(container.interfaces[0].address)
    for network in networks:
        config += "    network {} area 0\n".format(network)

    config += '    redistribute kernel\n'
    config += '    redistribute kernel\n'
    config += '    redistribute connected\n'
    config += '    redistribute static\n'
    config += '    default-information originate\n'
    config += "\n!\n"

    count = 1
    for interface in container.interfaces:
        if is_lxc(container.container_type):
            interface_name = "eth{}".format(count)
            count += 1
        else:
            interface_name = interface.interface_id
        config += "interface {}\n".format(interface_name)
        config += "    ip ospf hello-interval 1\n"
        config += "    ip ospf dead-interval 4\n"


    return config
