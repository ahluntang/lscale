#!/usr/bin/env python

import os, traceback, time, logging

from lxml.etree import ElementTree, Element, SubElement, tostring
from collections import defaultdict

def write_topology_xml(topology_root, output):
    root_tree = Element('data')
    hosts_tree = SubElement(root_tree,'hosts')
    for host_id, host in topology_root.items():

        host_tree        = SubElement(hosts_tree, 'host')
        hid_element      = SubElement(host_tree, 'id')
        hid_element.text = host_id

        containers_tree  = SubElement(host_tree, 'containers')
        links_tree       = SubElement(host_tree, 'links')
        bridges_tree     = SubElement(host_tree, 'bridges')


        links    = defaultdict(list)
        #bridges  = defaultdict(list)
        
        for (container_id, container) in host['containers'].items():

            container_tree   = SubElement(containers_tree, 'container')
            cid_element      = SubElement(container_tree, 'id')
            cid_element.text = container_id

            # get interfaces
            for interface in container.interfaces:
                link_id = interface.link_id
                interface.set_container(container.container_id)
                links[link_id].append(interface)
        
        link_trees = {}

        for link_id, interfaces in links.items():
            link_tree = None
            link_tree        = SubElement(links_tree, 'link')
            lid_element      = SubElement(link_tree, 'id')
            lid_element.text = link_id

            for interface in interfaces:
                if_element              = SubElement(link_tree, 'vinterface')
                ifid_element            = SubElement(if_element, 'id')
                ifid_element.text       = interface.interface_id
                container_element       = SubElement(if_element, 'container')
                container_element.text  = interface.container_id
                if(interface.address is not None):
                    address_element     = SubElement(if_element, 'address')
                    address_element.text= interface.address

        for bridge_id, bridge in host['bridges'].items():
            bridge_element      = SubElement(bridges_tree,'bridge')

            bid_element         = SubElement(bridge_element, 'id')
            bid_element.text    = bridge.bridge_id

            cid_element         = SubElement(bridge_element, 'container')
            cid_element.text    = bridge.container_id

            if (bridge.address != "0.0.0.0"):
                address_element     = SubElement(bridge_element, 'address')
                address_element.text= bridge.address

            interface_element   = SubElement(bridge_element, 'interfaces')

            for interface in bridge.interfaces:
                if_element     = SubElement(interface_element, 'interface')
                if_element.text= interface.interface_id




    print "\n\nEXPORT:\n"
    print tostring(root_tree, pretty_print=True)

    dir = 'output'
    if not os.path.exists( dir ) :
        os.makedirs( dir )

    filename = "%s/%s" % (dir, output)

    print "\nWriting to: %s\n" % filename

    ElementTree(root_tree).write(filename, pretty_print=True)
