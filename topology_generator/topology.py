#!/usr/bin/env python

import os, traceback, time, logging, itertools

import netaddr

from elements import Container, Bridge, NetworkInterface

class UsedResources(object):
    """ Saves amount of used resources.
    Class to track how many items have been created
    """
    def __init__(self, last_host, last_container_id, last_link_id):
        self.last_host       = 0
        self.last_bridge     = 0
        self.last_container  = 0
        self.last_link       = 0

    def get_new_host_id(self):
        self.last_host += 1
        return "h%03d" % self.last_host

    def get_new_bridge_id(self):
        self.last_bridge += 1
        return "b%03d" % self.last_bridge

    def get_new_container_id(self):
        self.last_container += 1
        return "c%03d" % self.last_container

    def get_new_link_id(self):
        self.last_link += 1
        return "l%03d" % self.last_link



class NetworkComponent(object):
    """Represents a part of the network.

    """
    new_id = itertools.count().next

    def __init__(self):
        self.component_id           = NetworkComponent.new_id()
        self.host_id                = None
        self.type                   = None
        self.free_link_interfaces   = []
        self.has_free_interfaces    = []

        self.topology   = {}

        self.topology['containers'] = {}
        self.topology['bridges']    = {}




def add_component_to_topology(topology_root, component):
    host_id = component.host_id

    for container_id, container in component.topology['containers'].items():
        topology_root[host_id]['containers'][container.container_id] = container

    for bridge_id, bridge in component.topology['bridges'].items():
        topology_root[host_id]['bridges'][bridge.bridge_id] = bridge

def set_resources(resources):
   global used_resources
   used_resources = resources

def add_host(topology_root):
    # lets start with adding a host.
    host_id = used_resources.get_new_host_id()
    host = Container(host_id, True)

    topology_root[host_id]               = {}
    topology_root[host_id]['id']         = host
    topology_root[host_id]['containers'] = {}
    #topology_root[host_id]['links']      = {}
    topology_root[host_id]['bridges']    = {}

    return host_id

def define_topology_component(component, host_id, connected_to = None):
    component.host_id = host_id
    # type of topology: ring, star or mesh
    toptype = topology_type()
    containers_number = number_of_containers()
    #subnet_config = subnetting(containers)
    
    # define some containers
    if (toptype == 'ring'):
        create_ring(host_id, component, containers_number)
    if (toptype == 'bridge'):
        create_bridge(component)
    
def connect_components(comp1, comp2):
    if( comp1.type == "bridge" and comp2.type == "bridge" ):
        connect_bridges(comp1,comp2)
    elif( comp1.type == "bridge" and comp2.type == "ring" ):
        connect_ring_bridge(comp2,comp1)
    elif( comp1.type == "ring" and comp2.type == "bridge" ):
        connect_ring_bridge(comp1,comp2)

def connect_ring_bridge(ring_component, bridge_component):
    link_id = used_resources.get_new_link_id()

    ring_container = ring_component.has_free_interfaces.pop()

    ring_interface = ring_component.free_link_interfaces.pop()

    br = bridge_component.has_free_interfaces[0]
    bridge_interface_id   = "%s.%03d" % ( br.bridge_id, br.get_next_interface() )

    bridge_interface      = NetworkInterface(bridge_interface_id, link_id)

    br.add_interface(ring_interface)
    ring_container.add_interface(bridge_interface)
    

def connect_bridges(bridge1_component, bridge2_component):
    link_id = used_resources.get_new_link_id()

    br1 = bridge1_component.has_free_interfaces[0]
    br2 = bridge2_component.has_free_interfaces[0]

    interface1_id   = "%s.%03d" % ( br1.bridge_id, br1.get_next_interface() )
    interface1      = NetworkInterface(interface1_id, link_id)

    interface2_id   = "%s.%03d" % ( br2.bridge_id, br2.get_next_interface() )
    interface2      = NetworkInterface(interface2_id, link_id)

    br1.add_interface(interface2)
    br2.add_interface(interface1)

def topology_type():
    default     = 'ring'
    prompt      = "Select type of topology: ring, star or mesh (%s): " % default
    response    = raw_input(prompt).rstrip().lower()

    while True:
        if ( response == 'ring' or response == 'star' or  response == 'mesh'):
            return response
        elif (response == '' ):
            return default
        else:
            response = raw_input(prompt).rstrip().lower()

def number_of_containers():
    default     = 5
    prompt      = "Select amount to containers to add (%s): " % default
    response    = raw_input(prompt).rstrip().lower()

    while True:
        if ( response.isdigit() and response > 0 ):
            return response
        elif (response == '' ):
            return default
        else:
            response = raw_input(prompt).rstrip().lower()


def create_bridge(host_id, component, connected_to = None):
    """ Creates a bridge.
    Optionally adds an interface from connected_to to the bridge.
    """
    logging.getLogger(__name__).info("Creating bridgecomponent (%s)", component.component_id)
    component.host_id   = host_id
    component.type      = "bridge"

    bridge_id           = used_resources.get_new_bridge_id()
    bridge              = Bridge(bridge_id)
    bridge.container_id = host_id

    component.topology['bridges'][bridge_id] = bridge
    
    # bridges are added to the free interfaces list
    component.has_free_interfaces.append(bridge)


def create_ring(host_id, component):
    component.host_id = host_id
    component.type = "ring"

    containers_number = number_of_containers()

    logging.getLogger(__name__).info("Creating ring with %s containers.", containers_number)
    network = None
    subnet = subnet_ring(containers_number)
	
    ip_address = None

    if (subnet is not None):
        ip_address = ip_scheme(subnet)

        address = "%s/%s" % (ip_address, subnet)
        network = netaddr.IPNetwork(address)

    containers = component.topology['containers']
    first_container = None
    last_container = None
    # creating all containers
    for i in range(0, containers_number):
        container_id    = used_resources.get_new_container_id()
        if (i == 0):
            first_container = container_id
        elif(i == containers_number-1 ):
            last_container = container_id
        c                           = Container(container_id)
        containers[container_id]    = c

        logging.getLogger(__name__).info("Created container %s in %s", container_id, host_id)

        # create links between the containers
        if (i > 0):
            c2              = containers[last_container_id]
            link_id         = used_resources.get_new_link_id()

            interface1_id   = "%s.1" % last_container_id
            interface1      = NetworkInterface(interface1_id, link_id)

            interface2_id   = "%s.0" % container_id 
            interface2      = NetworkInterface(interface2_id, link_id)

            # TODO: add code for optional ip addressing

            # adding interfaces to the previous and this container
            c2.add_interface(interface1)
            c.add_interface(interface2)
            logging.getLogger(__name__).info("Created link %s. Connections: %s->%s and %s->%s ", link_id, interface1.interface_id, c2.container_id, interface2.interface_id, c.container_id)

        last_container_id               = container_id

    # close ring or not
    print "Ring component created, do you want to close it or not?"
    print " * If you close the ring, a link will be added between first and last container."
    print " * If you keep the ring open, there will be two unused interfaces in this component."
    prompt      = "Type open or close (open) : "
    response = raw_input(prompt).rstrip().lower()

    interface1_id   = "%s.0" % first_container
    interface1      = NetworkInterface(interface1_id, link_id)

    interface2_id   = "%s.1" % last_container 
    interface2      = NetworkInterface(interface2_id, link_id)

    while True:
        if( response == "open" or response == "" ):
            component.free_link_interfaces.append(interface1)
            component.free_link_interfaces.append(interface2)
            component.has_free_interfaces.append(containers[first_container])
            component.has_free_interfaces.append(containers[last_container])
            return
        elif( response == "close" ):
            # close the ring
            containers[first_container].add_interface(interface1)
            containers[last_container].add_interface(interface2)
            return
        else:
            response = raw_input(prompt).rstrip().lower()


def subnet_ring(containers):
    default = 30
    print "\n Select netmask. "
    print " * There are %d containers." % containers
    print " * In (open)ring topologies, each link between the containers will be configured as a new subnet."
    print " * For normal (open)ring topologies, each link will need network address, broadcast address and two addresses for each endpoint."
    print " * Recommended netmask for this is /30."
    print " * Type 'none' if you want to manually configure ip addressing scheme\n"

    prompt = "Select the netmask for this network with %s containers (%s): " % (containers, default)
    response = raw_input(prompt).rstrip().lower()
    while True:
        if ( response.isdigit() and response > 2 and response < 32 ):
            return response
        elif (response == 'none'):
        	return None
        elif (response == '' ):
         	return default
        else:
            response = raw_input(prompt).rstrip().lower()

def ip_scheme(subnet_config):
    default = '172.16.0.0'

    prompt = "Select the network address you want to use for the containers (%s)" % default
    response = raw_input(prompt).rstrip().lower()

    while True:
    	try:
            if(response == ''):
                return default
            else:
                ip_address = netaddr.IPAddress(response)
                return response
        except Exception, e:
            response = raw_input(prompt).rstrip().lower()
        
