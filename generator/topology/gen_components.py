#!/usr/bin/env python
# -*- coding: utf-8 -*-


import logging

import netaddr

from generator.topology.elements import NetworkComponent, Container, Bridge, NetworkInterface
from utilities.lscale import ContainerType
import utilities.exceptions as exceptions


def add_component_to_topology(topology_root, component):
    """ Adds component to main topology

    :param topology_root: main topology
    :param component: component to add to topology
    """
    logging.getLogger(__name__).info("Adding component %s (%s) to main topology", component.component_id,
                                     component.type)

    host_id = component.host_id

    for container_id, container in component.topology['containers'].items():
        topology_root[host_id]['containers'][container.container_id] = container
    for bridge_id, bridge in component.topology['bridges'].items():
        topology_root[host_id]['bridges'][bridge.bridge_id] = bridge


def set_resources(resources):
    """ Sets the resources in the global module variable used_resources.

     resources will be used to know from where new id generation can be started.
    :param resources:
    """
    global used_resources
    used_resources = resources


def get_resources():
    global used_resources
    return used_resources


def add_host(topology_root):
    """ Adds host to main topology.

    :param topology_root: the main topology
    :return: returns host_id
    """

    host_id = used_resources.get_new_host_id()
    host = Container(host_id, ContainerType.NONE)

    host.preroutingscript = "host_pre_routing.sh"
    host.routingscript = "host_routing.sh"
    host.postroutingscript = "host_post_routing.sh"
    host.cleanupscript = "host_cleanup.sh"

    topology_root[host_id] = {}
    topology_root[host_id]['id'] = host
    topology_root[host_id]['containers'] = {}
    topology_root[host_id]['containers'][host_id] = host
    #topology_root[host_id]['links']      = {}
    topology_root[host_id]['bridges'] = {}

    return host_id


def add_management_interface(host, component, addressing_scheme=None):
    """

    :param host:
    :param component:
    :param addressing_scheme:
    """
    link_id = used_resources.get_new_link_id()
    host_interface_id = "m%s.%03d" % (host.container_id, host.get_next_interface() )
    host_interface = NetworkInterface(host_interface_id, link_id)

    if addressing_scheme is not None:
        ip = addressing_scheme['bridge_links'].pop()
        host_interface.address = "%s/%s" % (ip, addressing_scheme['bridge_prefix'])

    bridge = None
    if component.type == "bridge":
        bridge = component.connection_points[0]
        interface_id = bridge.bridge_id

    # get bridge and interface for bridge
    br = component.connection_points[0]
    bridge_interface_id = "%s.%03d" % (br.bridge_id, br.get_next_interface())

    bridge_interface = NetworkInterface(bridge_interface_id, link_id)

    host_interface.summarizes = [netaddr.IPNetwork("0.0.0.0/0")]
    print("link %s has %s and %s" % (link_id, host_interface.interface_id, bridge_interface.interface_id))

    br.add_interface(bridge_interface)
    host.add_interface(host_interface)


def connect_components(comp1, comp2, addressing_scheme=None):
    """ Connects two components together.

    If each of the components has 1 or more free interfaces, this method will create a link between them using
    the free interfaces.

    :param comp1: first component
    :param comp2: second component
    """
    if comp1.type == "bridge" and comp2.type == "bridge":
        # two bridges, both are single element components, directly select the bridge from the connection_points list.
        connect_bridges(comp1.connection_points[0], comp2.connection_points[0])
    elif comp1.type == "bridge" and comp2.type == "line":
        connect_line_bridge(comp2, comp1, addressing_scheme)
    elif comp1.type == "line" and comp2.type == "bridge":
        connect_line_bridge(comp1, comp2, addressing_scheme)


def connect_elements(element_from, element_to, component_from=None, component_to=None, addressing_scheme=None):
    """

    :param element_from:
    :param component_from:
    :param element_to:
    :param component_to:
    :return:
    """
    both_containers = type(element_from) is Container and type(element_to) is Container
    container_and_bridge = type(element_from) is Container and type(element_to) is Bridge
    bridge_and_container = type(element_from) is Bridge and type(element_to) is Container
    both_bridges = type(element_from) is Bridge and type(element_to) is Container
    if both_containers:
        connect_containers(element_from, element_to, component_from, component_to, addressing_scheme)
    elif container_and_bridge:
        connect_container_bridge(element_from, element_to, component_from, addressing_scheme)
    elif bridge_and_container:
        connect_container_bridge(element_to, element_from, component_to, addressing_scheme)
    elif both_bridges:
        connect_bridges(element_from, element_to)
    else:
        pass


def connect_containers(c1, c2, c1_component=None, c2_component=None, addressing_scheme=None):
    link_id = used_resources.get_new_link_id()

    c1_interface_id = "%s.%03d" % (c1.container_id, c1.get_next_interface() )
    c1_interface = NetworkInterface(c1_interface_id, link_id)

    c2_interface_id = "%s.%03d" % (c2.container_id, c2.get_next_interface() )
    c2_interface = NetworkInterface(c2_interface_id, link_id)

    if addressing_scheme is not None:
        prefix = addressing_scheme['host_prefix']
        network = addressing_scheme['host_links'].pop()

        address = "%s/%s" % (network[1], prefix)
        c1_interface.address = address
        if c1_component is not None:
            c1_component.addresses.append(address)

        address = "%s/%s" % (network[2], prefix)
        c2_interface.address = address
        if c2_component is not None:
            c2_component.addresses.append(address)

    c1.add_interface(c1_interface)
    c2.add_interface(c2_interface)


def connect_container_bridge(container, bridge, container_component=None, addressing_scheme=None):
    link_id = used_resources.get_new_link_id()

    container_interface_id = "%s.%03d" % (container.container_id, container.get_next_interface() )
    container_interface = NetworkInterface(container_interface_id, link_id)

    bridge_interface_id = "%s.%03d" % (bridge.bridge_id, bridge.get_next_interface() )
    bridge_interface = NetworkInterface(bridge_interface_id, link_id)

    if addressing_scheme is not None:
        prefix = addressing_scheme['bridge_links']
        network = addressing_scheme['bridge_links'].pop()

        address = "%s/%s" % (network[0], prefix)
        container_interface.address = address

        if container_component is not None:
            container_component.addresses.append(address)

    container.add_interface(container_interface)
    bridge.add_interface(bridge_interface)


def connect_line_bridge(line_component, bridge_component, addressing_scheme=None):
    """ Connects a ring to a bridge.

    :param line_component: ring component that will be connected to the bridge. Needs at least two free interfaces
    :param bridge_component: bridge component that will be connected to the ring. Will add new interfaces to the bridge.
    """
    link_id = used_resources.get_new_link_id()

    line_container = line_component.connection_points.pop()

    # create new interface for container in line
    line_interface_id = "%s.%03d" % (line_container.container_id, line_container.get_next_interface() )
    line_interface = NetworkInterface(line_interface_id, link_id)
    if addressing_scheme is not None:
        ip = addressing_scheme['bridge_links'].pop()
        line_interface.address = "%s/%s" % (ip, addressing_scheme['bridge_prefix'])

    # get bridge and interface for bridge
    br = bridge_component.connection_points[0]
    bridge_interface_id = "%s.%03d" % ( br.bridge_id, br.get_next_interface() )

    bridge_interface = NetworkInterface(bridge_interface_id, link_id)

    # summary
    if addressing_scheme is not None:
        containers = len(line_component.topology['containers'])
        print("amount of containers: %s " % containers)
        other_container = None
        if len(line_component.connection_points) > 0:
            other_container = line_component.connection_points[0]
            line_component.addresses = sorted(line_component.addresses)

        if other_container is not None and netaddr.IPNetwork(line_container.interfaces[0].address) > netaddr.IPNetwork(
                other_container.interfaces[0].address):
            summary = netaddr.cidr_merge(line_component.addresses[(containers - 1):len(line_component.addresses)])
            line_component.addresses = line_component.addresses[0: containers - 2]
            print("2: ", )
            for address in line_component.addresses:
                print(address, )
        else:
            summary = netaddr.cidr_merge(line_component.addresses[0:containers - 2])
            line_component.addresses = line_component.addresses[containers - 1:len(line_component.addresses)]

        line_interface.summarizes = summary

    print("link %s has %s and %s" % (link_id, line_interface.interface_id, bridge_interface.interface_id))

    br.add_interface(bridge_interface)
    line_container.add_interface(line_interface)
    line_container.gateway = line_interface.interface_id


def connect_bridges(bridge_from, bridge_to):
    """ Connects two bridges together

    :param bridge_from: bridge component. Method adds new interface to this bridge.
    :param bridge_to: bridge component. Method adds new interface to this bridge.
    """

    link_id = used_resources.get_new_link_id()

    interface_from_id = "%s.%03d" % ( bridge_from.bridge_id, bridge_from.get_next_interface() )
    interface_from = NetworkInterface(interface_from_id, link_id)

    interface_to_id = "%s.%03d" % ( bridge_to.bridge_id, bridge_to.get_next_interface() )
    interface_to = NetworkInterface(interface_to_id, link_id)

    bridge_from.add_interface(interface_from)
    bridge_to.add_interface(interface_to)


def create_bridge(host, bridgetype="brctl"):
    """Creates a bridge.
    Optionally adds an interface from connected_to to the bridge.

    :param host:
    """
    component = NetworkComponent()
    logging.getLogger(__name__).info("Creating bridgecomponent (%s)", component.component_id)
    component.host_id = host.container_id
    component.type = "bridge"

    bridge_id = used_resources.get_new_bridge_id()
    bridge = Bridge(bridge_id, bridge_type=bridgetype)
    bridge.container_id = host.container_id

    component.topology['bridges'][bridge_id] = bridge

    # bridges are added to the connection points list
    component.connection_points.append(bridge)
    return component


def create_container(host, containertype=ContainerType.UNSHARED):
    component = NetworkComponent()
    logging.getLogger(__name__).info("Creating containercomponent (%s)", component.component_id)
    component.host_id = host.container_id
    component.type = "container"

    container_id = used_resources.get_new_container_id()
    container = Container(container_id, containertype)
    container.container_id = host.container_id

    component.topology['containers'][container_id] = container

    # add container to the connection points list
    component.connection_points.append(container)
    return component


def create_bus(host, amount_of_containers=5, addressing_scheme=None):
    """ Creates a bus component

    :param host:
    :param amount_of_containers: number of containers the star should create
    :param addressing_scheme: addressing scheme to use to set ip addresses of the interfaces
    """
    component = NetworkComponent()
    component.host_id = host.container_id
    component.type = "bus"

    logging.getLogger(__name__).info("Creating bus with %s containers.", amount_of_containers)

    bridge_address = None
    prefix = None
    network = None

    if addressing_scheme is not None:
        prefix = addressing_scheme['host_prefix']
        network = addressing_scheme['host_links'].pop()
        bridge_address = "%s/%s" % (network[1], prefix)
        component.addresses.append(bridge_address)

    # create a bridge

    bridge_id = used_resources.get_new_bridge_id()
    bridge = Bridge(bridge_id, bridge_address)
    bridge.container_id = component.host_id

    component.topology['bridges'][bridge_id] = bridge

    # add bridge as connection point for new connections to this star
    component.connection_points.append(bridge)

    containers = component.topology['containers']

    # make containers and link them to the new bridge
    for i in range(2, amount_of_containers + 2):
        container_id = "s%03d.%s" % (component.component_id, used_resources.get_new_container_id() )
        c = Container(container_id)
        containers[container_id] = c
        c.preroutingscript = "bus_pre_routing.sh"
        c.routingscript = "bus_routing.sh"
        c.postroutingscript = "bus_post_routing.sh"

        link_id = used_resources.get_new_link_id()

        container_interface_id = "%s.%03d" % (c.container_id, c.get_next_interface() )
        container_interface = NetworkInterface(container_interface_id, link_id)
        if addressing_scheme is not None:
            address = "%s/%s" % (network[i], prefix)
            container_interface.address = address
            component.addresses.append(address)

        bridge_interface_id = "%s.%03d" % (bridge.bridge_id, bridge.get_next_interface() )
        bridge_interface = NetworkInterface(bridge_interface_id, link_id)

        c.add_interface(container_interface)
        bridge.add_interface(bridge_interface)
    return component


def create_star(host, amount_of_containers=5, addressing_scheme=None):
    """ Creates a star component

    :param amount_of_containers: number of containers the star should create
    :param addressing_scheme: addressing scheme to use to set ip addresses of the interfaces
    """
    component = NetworkComponent()
    component.host_id = host.container_id
    component.type = "star"

    logging.getLogger(__name__).info("Creating star with %s containers.", amount_of_containers)

    prefix = None

    if addressing_scheme is not None:
        prefix = addressing_scheme['host_prefix']

    containers = component.topology['containers']

    #create center container in as central point of the star
    container_id = "s%03d.%s" % (component.component_id, used_resources.get_new_container_id() )
    center = Container(container_id)
    center.preroutingscript = "star_pre_routing.sh"
    center.routingscript = "star_routing.sh"
    center.postroutingscript = "star_post_routing.sh"
    containers[container_id] = center

    # make containers and link them to the new bridge
    for i in range(2, amount_of_containers + 2):
        if addressing_scheme is not None:
            network = addressing_scheme['host_links'].pop()

        container_id = "s%03d.%s" % (component.component_id, used_resources.get_new_container_id() )
        c = Container(container_id)
        containers[container_id] = c
        c.preroutingscript = "star_pre_routing.sh"
        c.routingscript = "star_routing.sh"
        c.postroutingscript = "star_post_routing.sh"

        link_id = used_resources.get_new_link_id()

        container_interface_id = "%s.%03d" % (c.container_id, c.get_next_interface() )
        container_interface = NetworkInterface(container_interface_id, link_id)
        if addressing_scheme is not None:
            address = "%s/%s" % (network[2], prefix)
            container_interface.address = address
            component.addresses.append(address)

        center_interface_id = "%s.%03d" % (center.container_id, center.get_next_interface() )
        center_interface = NetworkInterface(center_interface_id, link_id)
        if addressing_scheme is not None:
            address = "%s/%s" % (network[1], prefix)
            center_interface.address = address
            component.addresses.append(address)

        c.add_interface(container_interface)
        center.add_interface(center_interface)
    return component


def create_line(host, amount_of_containers=5, addressing_scheme=None):
    return create_ring(host, amount_of_containers, addressing_scheme, True)


def create_ring(host, amount_of_containers=5, addressing_scheme=None, is_line=False):
    """ Creates a ring component.

    :param host:  the host where the ring should be added
    :param component: component where the ring should be created
    :param amount_of_containers: number of containers the ring should create
    :param addressing_scheme: addressing scheme to use to set ip addresses of the interfaces.
    :param is_line: sets whether the ring should be closed or not
        (acts as line if true, use it to connect the line endpoints to a different network)
    :return:
    """

    component = NetworkComponent()
    component.host_id = host.container_id
    if is_line:
        component.type = "line"
        logging.getLogger(__name__).info("Creating line with %s containers.", amount_of_containers)
    else:
        component.type = "ring"
        logging.getLogger(__name__).info("Creating ring with %s containers.", amount_of_containers)

    containers = component.topology['containers']

    # keep a reference to the first and last container.
    first_container = None
    last_container = None

    # create all containers
    for i in range(0, amount_of_containers):
        # get id for current container
        cur_container_id = "r%03d.%s" % (component.component_id, used_resources.get_new_container_id() )

        # keep a reference to the first and last container.
        if i == 0:
            first_container = cur_container_id
        elif i == amount_of_containers - 1:
            last_container = cur_container_id

        cur_container = Container(cur_container_id)

        cur_container.preroutingscript = "ring_pre_routing.sh"
        cur_container.routingscript = "ring_routing.sh"
        cur_container.postroutingscript = "ring_post_routing.sh"

        containers[cur_container_id] = cur_container

        logging.getLogger(__name__).info("Created container %s in %s", cur_container_id, host.container_id)

        # create links between the containers
        # each link has two interfaces
        if i > 0:
            prev_container = containers[previous_container_id]
            link_id = used_resources.get_new_link_id()

            interface_prev_id = "%s.%03d" % (previous_container_id, prev_container.get_next_interface() )
            interface_prev = NetworkInterface(interface_prev_id, link_id)

            interface_cur_id = "%s.%03d" % (cur_container_id, cur_container.get_next_interface() )
            interface_cur = NetworkInterface(interface_cur_id, link_id)

            if addressing_scheme is not None:
                try:
                    network = addressing_scheme['host_links'].pop()
                    if1_ip = "%s/%s" % (network[1], network.prefixlen)
                    if2_ip = "%s/%s" % (network[2], network.prefixlen)
                    interface_prev.address = if1_ip
                    interface_cur.address = if2_ip

                    # also add addresses to list in component
                    component.addresses.append(if1_ip)
                    component.addresses.append(if2_ip)
                except Exception as e:
                    raise exceptions.IPComponentException(e)

            # adding interfaces to the previous and this container
            prev_container.add_interface(interface_prev)
            cur_container.add_interface(interface_cur)

            logging.getLogger(__name__).info("Created link %s. Connections: %s->%s and %s->%s ", link_id,
                                             interface_prev.interface_id, prev_container.container_id,
                                             interface_cur.interface_id, cur_container.container_id)

        previous_container_id = cur_container_id

    if not is_line:
        # close line as ring
        interface_prev_id = "%s.%03d" % (first_container, containers[first_container].get_next_interface() )
        interface_prev = NetworkInterface(interface_prev_id, link_id)

        interface_cur_id = "%s.%03d" % (last_container, containers[last_container].get_next_interface() )
        interface_cur = NetworkInterface(interface_cur_id, link_id)

        if addressing_scheme is not None:
            network = addressing_scheme['host_links'].pop()
            if1_ip = "%s/%s" % (network[1], network.prefixlen)
            if2_ip = "%s/%s" % (network[2], network.prefixlen)
            interface_prev.address = if1_ip
            interface_cur.address = if2_ip

        containers[first_container].add_interface(interface_prev)
        containers[last_container].add_interface(interface_cur)
    else:
        # acts as line, no need to close, append the endpoints to the connection_points
        component.connection_points.append(containers[first_container])
        component.connection_points.append(containers[last_container])

    if addressing_scheme is not None:
        i = 0
        for cur_container_id, container in sorted(containers.items()):
            if i > 2:
                if1_routes = component.addresses[0:i]
                container.interfaces[0].routes.extend(if1_routes)

            if i <= amount_of_containers:
                if2_routes = component.addresses[i:len(component.addresses) + 1]
                if i > 0 and len(container.interfaces) > 1:
                    container.interfaces[1].routes.extend(if2_routes)
                else:
                    container.interfaces[0].routes.extend(if2_routes)

            if i < amount_of_containers / 2 :
                container.gateway = container.interfaces[0].interface_id
            elif len(container.interfaces) > 1:
                container.gateway = container.interfaces[1].interface_id
            else:
                container.gateway = container.interfaces[0].interface_id

            i += 2
    return component
