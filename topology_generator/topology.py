#!/usr/bin/env python
# -*- coding: utf-8 -*-


import logging, netaddr

from elements import Container, Bridge, NetworkInterface, UsedResources


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

    
def connect_components(comp1, comp2):

    """ Connects two components together.

    If each of the components has 1 or more free interfaces, this method will create a link between them using
    the free interfaces.

    :param comp1: first component
    :param comp2: second component
    """
    if( comp1.type == "bridge" and comp2.type == "bridge" ):
        connect_bridges(comp1,comp2)
    elif( comp1.type == "bridge" and comp2.type == "ring" ):
        connect_ring_bridge(comp2,comp1)
    elif( comp1.type == "ring" and comp2.type == "bridge" ):
        connect_ring_bridge(comp1,comp2)

def connect_ring_bridge(ring_component, bridge_component):
    """ Connects a ring to a bridge.

    :param ring_component: ring component that will be connected to the bridge. Needs at least two free interfaces
    :param bridge_component: bridge component that will be connected to the ring. Will add new interfaces to the bridge.
    """
    link_id = used_resources.get_new_link_id()

    ring_container = ring_component.connection_points.pop()

    # create new interface for container in ring
    ring_interface_id = "%s.%03d" % (ring_container.container_id , ring_container.get_next_interface() )
    ring_interface = NetworkInterface( ring_interface_id, link_id )

    # get bridge and interface for bridge
    br = bridge_component.connection_points[0]
    bridge_interface_id   = "%s.%03d" % ( br.bridge_id, br.get_next_interface() )

    bridge_interface      = NetworkInterface(bridge_interface_id, link_id)

    print "link %s has %s and %s" % (link_id, ring_interface.interface_id, bridge_interface.interface_id)

    br.add_interface(ring_interface)
    ring_container.add_interface(bridge_interface)
    

def connect_bridges(bridge1_component, bridge2_component):
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


def create_ring(host_id, component, containers_number = 5, addressing_scheme = None, close_ring = False):
    """ Creates a ring.

    :param host_id: id of the host where the ring should be added
    :param component: component where the ring should be created
    :param containers_number: number of containers the ring should create
    :param addressing_scheme: addressing scheme to use to set ip addresses of the interfaces.
    :param close_ring: sets whether the ring should be closed or not (keep it open to connect it to a different network)
    :return:
    """
    component.host_id = host_id
    component.type = "ring"

    logging.getLogger(__name__).info("Creating ring with %s containers.", containers_number)


    containers = component.topology['containers']
    first_container = None
    last_container = None
    # creating all containers
    for i in range(0, containers_number):
        container_id    = used_resources.get_new_container_id()
        if (i == 0):
            first_container = container_id
        elif(i == containers_number - 1 ):
            last_container = container_id

        c                           = Container(container_id)
        containers[container_id]    = c

        logging.getLogger(__name__).info("Created container %s in %s", container_id, host_id)

        # create links between the containers
        if (i > 0):
            c2              = containers[ previous_container_id ]
            link_id         = used_resources.get_new_link_id()

            interface1_id   = "%s.%03d" % (previous_container_id, c2.get_next_interface() )
            interface1      = NetworkInterface(interface1_id, link_id)

            interface2_id   = "%s.%03d" % (container_id, c.get_next_interface() )
            interface2      = NetworkInterface(interface2_id, link_id)

            if addressing_scheme is not None:
                network = addressing_scheme['host_links'].pop()
                if1_ip = "%s/%s" % (network[1], network.prefixlen)
                if2_ip = "%s/%s" % (network[2], network.prefixlen)
                interface1.address = if1_ip
                interface2.address = if2_ip

            # adding interfaces to the previous and this container
            c2.add_interface(interface1)
            c.add_interface(interface2)

            logging.getLogger(__name__).info("Created link %s. Connections: %s->%s and %s->%s ", link_id, interface1.interface_id, c2.container_id, interface2.interface_id, c.container_id)

        previous_container_id = container_id

    if close_ring:
        # close the ring
        interface1_id   = "%s.%03d" % (first_container, containers[first_container].get_next_interface() )
        interface1      = NetworkInterface(interface1_id, link_id)

        interface2_id   = "%s.%03d" % (last_container, containers[last_container].get_next_interface() )
        interface2      = NetworkInterface(interface2_id, link_id)

        if addressing_scheme is not None :
            network = addressing_scheme['host_links'].pop()
            if1_ip = "%s/%s" % (network[1], network.prefixlen)
            if2_ip = "%s/%s" % (network[2], network.prefixlen)
            interface1.address = if1_ip
            interface2.address = if2_ip

        containers[first_container].add_interface(interface1)
        containers[last_container].add_interface(interface2)
    else :
        component.connection_points.append(containers[first_container])
        component.connection_points.append(containers[last_container])
