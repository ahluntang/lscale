#!/usr/bin/env python

import os, traceback, time, logging

import ipcalc

from elements import Container, Bridge, NetworkInterface

class UsedResources(object):

    def __init__(self, last_container_id, last_link_id):
        self.last_container = 0
        self.last_link      = 0

def define_topology_details(used_resources):
	# type of topology: ring, star or mesh
	toptype = topology_type()
	containers = number_of_containers()
	#subnet_config = subnetting(containers)
	topology = {}
	if (toptype == 'openring'):
		topology = create_openring(containers, used_resources)



def topology_type():
    default = 'openring'

    prompt = "Select type of topology: ring, openring, star or mesh (%s): " % default

    response = raw_input(prompt).rstrip().lower()

    while True:
        if ( response == 'ring' or response == 'star' or  response == 'mesh'):
            return response
        elif (response == '' ):
            return default
        else:
            response = raw_input(prompt).rstrip().lower()

def number_of_containers():
    default = 5

    prompt = "Select amount to containers to add (%s): " % default
    response = raw_input(prompt)
    response = response.rstrip().lower()

    while True:
        if ( response.isdigit() and response > 0 ):
            return response
        elif (response == '' ):
            return default
        else:
            response = raw_input(prompt).rstrip().lower()

def create_openring(containers, used_resources):
    network = None
    subnet = subnet_ring(containers)
	
    ip_address = None

    if (subnet is not None):
        ip_address = ip_scheme(subnet)

        address = "%s/%s" % (ip_address, subnet)
        network = ipcalc.Network(address)

    
    created_containers = {}


    # creating all containers
    for i in range(0, containers):
        container_id = "c%03d" % used_resources.last_container
        c = Container(container_id)
        created_containers[container_id] = c

        # create links between the containers
        if (i > 0):
            c1 = created_containers[last_container_id]
            link_id = "link%s" % used_resources.last_link

            interface1_id   = "%s.1" % last_container_id
            interface1      = NetworkInterface(interface1_id, link_id)

            interface2_id   = "%s.0" % container_id 
            interface2      = NetworkInterface(interface2_id, link_id)

            # adding interfaces to the previous and this container
            c1.add_interface(interface1)
            c.add_interface(interface2)

            used_resources.last_link += 1

        last_container_id               = container_id
        used_resources.last_container  += 1

    
    #for (container_id, container) in created_containers.items() :
    #    print "%s: " % container_id,
    #    for interface in container.interfaces:
    #        if (interface.address is None):
    #            address = ""
    #        else:
    #            address = interface.address
    #        print "%s/%s/%s" % (interface.interface_id, interface.link_id, address ),
    #    print ""
    
    return created_containers



def subnet_ring(containers):
    default = 30
    print "There are %d containers.\n" % containers
    print "In (open)ring topologies, each link between the containers will be configured as a new subnet."
    print "For normal (open)ring topologies, each link will need network address, broadcast address and two addresses for each endpoint."
    print "Recommended netmask for this is /30."
    print "Type 'none' if you want to manually configure ip addressing scheme\n"

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
        
