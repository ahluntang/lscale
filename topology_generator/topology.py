#!/usr/bin/env python

import os, traceback, time, logging

import ipcalc



def define_topology_details():
	# type of topology: ring, star or mesh
	toptype = topology_type()
	containers = number_of_containers()
	#subnet_config = subnetting(containers)
	topology = {}
	if (toptype == 'openring'):
		topology = create_openring(containers)



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
    response = raw_input(prompt).rstrip().lower()

    while True:
        if ( response.isdigit() and response > 0 ):
            return response
         elif (response == '' ):
         	return default
        else:
            response = raw_input(prompt).rstrip().lower()

def create_openring(containers):
	network = None
	subnet = subnet_ring(containers)
	
	ip_address = None

	if (subnet_config is not None):
		ip_address = ip_scheme(subnet_config)

		address = "%s/%s" % (ip_address, subnet)
		network = ipcalc.Network(address)

	



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
	default = 172.16.0.0

	prompt "Select the network address you want to use for the containers (%s)" % default
	response = raw_input(prompt).rstrip().lower()

    while True:
    	try:
    		ip_address = ipcalc.IP(response)

    		if(response == ''):
    			return default
    		else:
    			return response

    	except Exception, e:
    		response = raw_input(prompt).rstrip().lower()
        
