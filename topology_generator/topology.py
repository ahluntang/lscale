#!/usr/bin/env python

import os, traceback, time, logging

import ipcalc

from elements import Container, Bridge, NetworkInterface

class UsedResources(object):
    """ Saves amount of used resources.
    Class to track how many items have been created
    """
    def __init__(self, last_host, last_container_id, last_link_id):
        self.last_host      = 0
        self.last_container = 0
        self.last_link      = 0

def define_topology_details(used_resources):
    topology = {}
    
    host_id = add_host(used_resources, topology)

    # create component in topology
    define_topology_component(used_resources, topology, host_id)


    return topology

def add_host(used_resources, topology):
    # lets start with adding a host.
    host_id = "h%03d" % used_resources.last_host
    host = Container(host_id, True)
    used_resources.last_host += 1

    topology[host_id] = {}
    topology[host_id]['id'] = host
    topology[host_id]['containers'] = {}
    topology[host_id]['links'] = {}
    topology[host_id]['bridges'] = {}

    return host_id

def define_topology_component(used_resources, topology, host_id, connected_to = None):
    # type of topology: ring, star or mesh
    toptype = topology_type()
    containers_number = number_of_containers()
    #subnet_config = subnetting(containers)
    
    # define some containers
    if (toptype == 'ring'):
        create_ring(host_id, topology[host_id]['containers'], containers_number, used_resources)
    if (toptype == 'bridge'):
        create_bridge(topology[host_id]['bridges'])
    


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


def create_bridge(used_resources, connected_to = None):
    """ Creates a bridge.
    Optionally adds an interface from connected_to to the bridge.
    """
    pass


def create_ring(host_id, containers, containers_number, used_resources, connected_to = None):
    if connected_to is None:
        connected = "nothing"
    else:
        connected = connected_to
    logging.getLogger(__name__).info("Creating ring with %s containers. Connected to %s.", containers_number, connected)
    network = None
    subnet = subnet_ring(containers_number)
	
    ip_address = None

    if (subnet is not None):
        ip_address = ip_scheme(subnet)

        address = "%s/%s" % (ip_address, subnet)
        network = ipcalc.Network(address)


    # creating all containers
    for i in range(0, containers_number):
        container_id                = "c%03d" % used_resources.last_container
        c                           = Container(container_id)
        containers[container_id]    = c

        logging.getLogger(__name__).info("Created container %s in %s", container_id, host_id)

        # create links between the containers
        if (i > 0):
            c1              = containers[last_container_id]
            link_id         = "l%03d" % used_resources.last_link

            interface1_id   = "%s.1" % last_container_id
            interface1      = NetworkInterface(interface1_id, link_id)

            interface2_id   = "%s.0" % container_id 
            interface2      = NetworkInterface(interface2_id, link_id)
            # TODO: add code for optional ip addressing

            # adding interfaces to the previous and this container
            c1.add_interface(interface1)
            c.add_interface(interface2)
            logging.getLogger(__name__).info("Created link %s. Connections: %s->%s and %s->%s ", link_id, interface1.interface_id, c1.container_id, interface2.interface_id, c.container_id)

            used_resources.last_link += 1

        last_container_id               = container_id
        used_resources.last_container  += 1

    if (connected_to is None):
        # close the ring
        pass
    else:
        # connect the ring to connected_to
        pass



def subnet_ring(containers):
    default = 30
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
                ip_address = ipcalc.IP(response)
                return response
        except Exception, e:
            response = raw_input(prompt).rstrip().lower()
        
