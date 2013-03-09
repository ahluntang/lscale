#!/usr/bin/env python
# -*- coding: utf-8 -*-


import logging

import netaddr

from elements import Container, Bridge, NetworkInterface
import topology.exceptions as exceptions

def add_component_to_topology(topology_root, component):
    """ Adds component to main topology

    :param topology_root: main topology
    :param component: component to add to topology
    """
    logging.getLogger(__name__).info("Adding component %s (%s) to main topology", component.component_id, component.type)

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
    host = Container(host_id, True)

    topology_root[host_id]               = {}
    topology_root[host_id]['id']         = host
    topology_root[host_id]['containers'] = {}
    #topology_root[host_id]['links']      = {}
    topology_root[host_id]['bridges']    = {}

    return host_id


def connect_components(comp1, comp2, addressing_scheme = None):

    """ Connects two components together.

    If each of the components has 1 or more free interfaces, this method will create a link between them using
    the free interfaces.

    :param comp1: first component
    :param comp2: second component
    """
    if( comp1.type == "bridge" and comp2.type == "bridge" ):
        connect_bridges(comp1,comp2, addressing_scheme)
    elif( comp1.type == "bridge" and comp2.type == "ring" ):
        connect_ring_bridge(comp2,comp1, addressing_scheme)
    elif( comp1.type == "ring" and comp2.type == "bridge" ):
        connect_ring_bridge(comp1,comp2, addressing_scheme)


def connect_ring_bridge(ring_component, bridge_component, addressing_scheme = None):
    """ Connects a ring to a bridge.

    :param ring_component: ring component that will be connected to the bridge. Needs at least two free interfaces
    :param bridge_component: bridge component that will be connected to the ring. Will add new interfaces to the bridge.
    """
    link_id = used_resources.get_new_link_id()

    ring_container = ring_component.connection_points.pop()

    # create new interface for container in ring
    ring_interface_id = "%s.%03d" % (ring_container.container_id , ring_container.get_next_interface() )
    ring_interface = NetworkInterface( ring_interface_id, link_id )
    if addressing_scheme is not None:
        ip = addressing_scheme['bridge_links'].pop()
        ring_interface.address = "%s/%s" % (ip, addressing_scheme['bridge_prefix'])

    # get bridge and interface for bridge
    br = bridge_component.connection_points[0]
    bridge_interface_id   = "%s.%03d" % ( br.bridge_id, br.get_next_interface() )

    bridge_interface      = NetworkInterface(bridge_interface_id, link_id)

    # summary
    if addressing_scheme is not None:
        other_container = None
        if len(ring_component.connection_points) > 0 :
            other_container = ring_component.connection_points[0]

            ring_component.addresses = sorted(ring_component.addresses)

        if other_container is not None and netaddr.IPNetwork(ring_container.interfaces[0].address) > netaddr.IPNetwork(other_container.interfaces[0].address) :
            summary = netaddr.cidr_merge(ring_component.addresses[len(ring_component.addresses) / 2 :len(ring_component.addresses)])
            ring_component.addresses = ring_component.addresses[0 :len(ring_component.addresses) / 2]
        else :
            summary = netaddr.cidr_merge(ring_component.addresses[0 :len(ring_component.addresses) / 2])
            ring_component.addresses = ring_component.addresses[len(ring_component.addresses) / 2 :len(ring_component.addresses)]

        ring_interface.summarizes = summary


    print "link %s has %s and %s" % (link_id, ring_interface.interface_id, bridge_interface.interface_id)

    br.add_interface(bridge_interface)
    ring_container.add_interface(ring_interface)


def connect_bridges(bridge1_component, bridge2_component, addressing_scheme = None):
    """ Connects two bridges together

    :param bridge1_component: bridge component. Method adds new interface to this bridge.
    :param bridge2_component: bridge component. Method adds new interface to this bridge.
    """

    link_id = used_resources.get_new_link_id()

    br1 = bridge1_component.connection_points[0]
    br2 = bridge2_component.connection_points[0]

    interface1_id   = "%s.%03d" % ( br1.bridge_id, br1.get_next_interface() )
    interface1      = NetworkInterface(interface1_id, link_id)

    interface2_id   = "%s.%03d" % ( br2.bridge_id, br2.get_next_interface() )
    interface2      = NetworkInterface(interface2_id, link_id)

    br1.add_interface(interface2)
    br2.add_interface(interface1)


def topology_type():
    """ Prompts user for type of component
    Valid inputs are 'ring', 'star' or 'mesh'.

    :return: type of component: 'ring', 'star' or 'mesh'
    """
    default     = 'ring'
    prompt      = "Select type of component: ring, star or mesh (%s): " % default
    response    = raw_input(prompt).rstrip().lower()

    while True:
        if ( response == 'ring' or response == 'star' or  response == 'mesh'):
            return response
        elif (response == '' ):
            return default
        else:
            response = raw_input(prompt).rstrip().lower()


def create_bridge(host_id, component):
    """Creates a bridge.
    Optionally adds an interface from connected_to to the bridge.

    :param host_id: id of the host where the bridge should be added.
    :param component: component where the bridge should be created.
    """
    logging.getLogger(__name__).info("Creating bridgecomponent (%s)", component.component_id)
    component.host_id   = host_id
    component.type      = "bridge"

    bridge_id           = used_resources.get_new_bridge_id()
    bridge              = Bridge(bridge_id)
    bridge.container_id = host_id

    component.topology['bridges'][bridge_id] = bridge

    # bridges are added to the free interfaces list
    component.connection_points.append(bridge)


def create_bus(host_id, component, containers_number = 5, addressing_scheme = None):
    """ Creates a bus component

    :param host_id: id of the host where the star should be added
    :param component: component where the star should be created
    :param containers_number: number of containers the star should create
    :param addressing_scheme: addressing scheme to use to set ip addresses of the interfaces
    """
    component.host_id = host_id
    component.type = "bus"

    logging.getLogger(__name__).info("Creating bus with %s containers.", containers_number)

    bridge_address = None
    prefix = None
    network = None

    if addressing_scheme is not None:
        prefix  = addressing_scheme['host_prefix']
        network = addressing_scheme['host_links'].pop()
        bridge_address = "%s/%s" % (network[1], prefix)
        component.addresses.append(bridge_address)

    # create a bridge

    bridge_id           = used_resources.get_new_bridge_id()
    bridge              = Bridge(bridge_id, bridge_address)
    bridge.container_id = component.host_id

    component.topology['bridges'][bridge_id] = bridge

    # add bridge as connection point for new connections to this star
    component.connection_points.append(bridge)


    containers = component.topology['containers']

    # make containers and link them to the new bridge
    for i in range(2, containers_number + 2) :
        container_id = "s%03d.%s" % (component.component_id, used_resources.get_new_container_id() )
        c = Container(container_id)
        containers[container_id ] = c
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


def create_star(host_id, component, containers_number = 5, addressing_scheme = None) :
    """ Creates a star component

    :param host_id: id of the host where the star should be added
    :param component: component where the star should be created
    :param containers_number: number of containers the star should create
    :param addressing_scheme: addressing scheme to use to set ip addresses of the interfaces
    """
    component.host_id = host_id
    component.type = "star"

    logging.getLogger(__name__).info("Creating star with %s containers.", containers_number)

    prefix = None

    if addressing_scheme is not None :
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
    for i in range(2, containers_number + 2) :
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
        if addressing_scheme is not None :
            address = "%s/%s" % (network[2], prefix)
            container_interface.address = address
            component.addresses.append(address)

        center_interface_id = "%s.%03d" % (center.container_id, center.get_next_interface() )
        center_interface = NetworkInterface(center_interface_id, link_id)
        if addressing_scheme is not None :
            address = "%s/%s" % (network[1], prefix)
            center_interface.address = address
            component.addresses.append(address)


        c.add_interface(container_interface)
        center.add_interface(center_interface)


def create_ring(host_id, component, containers_number = 5, addressing_scheme = None, is_line = True):
    """ Creates a ring component.

    :param host_id: id of the host where the ring should be added
    :param component: component where the ring should be created
    :param containers_number: number of containers the ring should create
    :param addressing_scheme: addressing scheme to use to set ip addresses of the interfaces.
    :param is_line: sets whether the ring should be closed or not
        (acts as line if true, use it to connect the line endpoints to a different network)
    :return:
    """
    component.host_id = host_id
    component.type = "ring"

    logging.getLogger(__name__).info("Creating ring with %s containers.", containers_number)


    containers = component.topology['containers']

    # keep a reference to the first and last container.
    first_container = None
    last_container = None

    # create all containers
    for i in range(0, containers_number):
        # get id for current container
        cur_container_id    = "r%03d.%s" % (component.component_id, used_resources.get_new_container_id() )

        # keep a reference to the first and last container.
        if (i == 0):
            first_container = cur_container_id
        elif(i == containers_number - 1 ):
            last_container = cur_container_id

        cur_container = Container(cur_container_id)

        cur_container.preroutingscript  = "ring_pre_routing.sh"
        cur_container.routingscript     = "ring_routing.sh"
        cur_container.postroutingscript = "ring_post_routing.sh"

        containers[cur_container_id] = cur_container

        logging.getLogger(__name__).info("Created container %s in %s", cur_container_id, host_id)

        # create links between the containers
        # each link has two interfaces
        if (i > 0):
            prev_container  = containers[ previous_container_id ]
            link_id         = used_resources.get_new_link_id()

            interface_prev_id = "%s.%03d" % (previous_container_id, prev_container.get_next_interface() )
            interface_prev    = NetworkInterface(interface_prev_id, link_id)

            interface_cur_id  = "%s.%03d" % (cur_container_id, cur_container.get_next_interface() )
            interface_cur     = NetworkInterface(interface_cur_id, link_id)

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
                except Exception, e:
                    raise exceptions.IPComponentException(Exception,e)

            # adding interfaces to the previous and this container
            prev_container.add_interface(interface_prev)
            cur_container.add_interface(interface_cur)

            logging.getLogger(__name__).info("Created link %s. Connections: %s->%s and %s->%s ", link_id, interface_prev.interface_id, prev_container.container_id, interface_cur.interface_id, cur_container.container_id)

        previous_container_id = cur_container_id

    if not is_line:
        # close line as ring
        interface_prev_id   = "%s.%03d" % (first_container, containers[first_container].get_next_interface() )
        interface_prev      = NetworkInterface(interface_prev_id, link_id)

        interface_cur_id   = "%s.%03d" % (last_container, containers[last_container].get_next_interface() )
        interface_cur      = NetworkInterface(interface_cur_id, link_id)

        if addressing_scheme is not None :
            network = addressing_scheme['host_links'].pop()
            if1_ip = "%s/%s" % (network[1], network.prefixlen)
            if2_ip = "%s/%s" % (network[2], network.prefixlen)
            interface_prev.address = if1_ip
            interface_cur.address = if2_ip

        containers[first_container].add_interface(interface_prev)
        containers[last_container].add_interface(interface_cur)
    else :
        # acts as line, no need to close, append the endpoints to the connection_points
        component.connection_points.append(containers[first_container])
        component.connection_points.append(containers[last_container])

    if addressing_scheme is not None:
        i = 0
        for cur_container_id, container in sorted(containers.items()):
            if(i > 2):
                if1_routes = component.addresses[0:i]
                container.interfaces[0].routes.extend(if1_routes)

            if (i <= containers_number) :
                if2_routes = component.addresses[i:len(component.addresses)+1]
                if i > 0 and len(container.interfaces) > 1 :
                    container.interfaces[1].routes.extend(if2_routes)
                else:
                    container.interfaces[0].routes.extend(if2_routes)


            if(i < containers_number/2 ):
                container.gateway = container.interfaces[0].interface_id
            elif len(container.interfaces) > 1:
                container.gateway = container.interfaces[1].interface_id
            else:
                container.gateway = container.interfaces[0].interface_id

            i += 2
